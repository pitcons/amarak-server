# encoding: utf8
import time
from config import CONFIG
from sqlalchemy import Integer, Text, String, Column, create_engine, Table
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Session, scoped_session
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class ReprNameMixin(object):

    def __repr__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.name


class ReprUriMixin(object):

    def __repr__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.uri


class Language(Base, ReprNameMixin):
    __table__ = Table(
        'language', Base.metadata,
        Column('id', Integer, primary_key=True),
        Column('lang', String(64), primary_key=True),
        Column('name', String(255), nullable=False),
    )


class Scheme(Base, ReprUriMixin):
    __table__ = Table(
        'scheme', Base.metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(64), nullable=False),
        Column('ns_prefix', String(512), nullable=False),
        Column('ns_url', String(512), nullable=False),
        Column('namespaces', Text(), nullable=False, server_default=''),
    )
    labels = relationship("SchemeLabel")


class SchemeLabel(Base):
    __table__ = Table(
        'scheme_label', Base.metadata,
        Column('id', Integer, primary_key=True),
        Column('scheme_id',
               Integer,
               ForeignKey("scheme.id", ondelete='cascade'),
               nullable=False),
        Column('lang', String(64), nullable=False),
        Column('label', String(512), nullable=False),
    )


class SchemeHierarchy(Base):
    __table__ = Table(
        'scheme_hierarchy', Base.metadata,
        Column('id', Integer, primary_key=True),
        Column('weight', Integer, default=0),
        Column('scheme_id',
               Integer,
               ForeignKey("scheme.id", ondelete='cascade'),
               nullable=False),
        Column('parent_id',
               Integer,
               ForeignKey("scheme.id", ondelete='cascade'),
               nullable=False),
        UniqueConstraint('scheme_id', 'parent_id')
    )


class Concept(Base, ReprUriMixin):
    __table__ = Table(
        'concept', Base.metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(512), nullable=False),
        Column('scheme_id',
               Integer,
               ForeignKey("scheme.id", ondelete='cascade'),
               nullable=False),
    )
    labels = relationship("ConceptLabel")
    links = relationship("ConceptLink",
                         foreign_keys='ConceptLink.concept1_id')
    def skos_name(self):
        return self.uri.replace(' ', '_').replace('"', '')


class ConceptLabel(Base):
    __table__ = Table(
        'concept_label', Base.metadata,
        Column('id', Integer, primary_key=True),
        Column('concept_id',
               Integer,
               ForeignKey("concept.id", ondelete='cascade'),
               nullable=False),
        Column('type', String(64), nullable=False),
        Column('lang', String(64), nullable=False),
        Column('label', String(512), nullable=False, index=True),
    )


# class ConceptInScheme(Base):
#     __table__ = Table(
#         'concept_in_scheme', Base.metadata,
#         Column('id', Integer, primary_key=True),
#         Column('concept_id',
#                Integer,
#                ForeignKey("concept.id", ondelete='cascade'),
#                nullable=False,
#                index=True),
#         Column('scheme_id',
#                Integer,
#                ForeignKey("scheme.id", ondelete='cascade'),
#                nullable=False,
#                index=True),
#     )


class ConceptRelation(Base):
    __table__ = Table(
        'concept_relation', Base.metadata,
        Column('id', Integer, primary_key=True),
        Column('scheme_id',
               Integer,
               ForeignKey("scheme.id", ondelete='cascade'),
               nullable=False),
        Column('name', String(64)),
        UniqueConstraint('scheme_id', 'name'),
    )


class ConceptLink(Base):
    __table__ = Table(
        'concept_link', Base.metadata,
        Column('id', Integer, primary_key=True),
        Column('concept1_id',
               Integer,
               ForeignKey("concept.id", ondelete='cascade'),
               nullable=False),
        Column('concept2_id',
               Integer,
               ForeignKey("concept.id", ondelete='cascade'),
               nullable=False),
        Column('concept_relation_id',
               Integer,
               ForeignKey("concept_relation.id", ondelete='cascade'),
               nullable=False),
        Column('scheme_id',
               Integer,
               ForeignKey("scheme.id", ondelete='cascade'),
               nullable=False),
        UniqueConstraint('concept_relation_id',
                         'concept1_id',
                         'concept2_id')
    )
    relation = relationship("ConceptRelation")
    concept1 = relationship("Concept",
                             foreign_keys="ConceptLink.concept1_id")
    concept2 = relationship("Concept",
                             foreign_keys="ConceptLink.concept2_id")


from sqlalchemy_utils import (database_exists,
                              create_database,
                              drop_database)
engine = create_engine(
    CONFIG.get('database', 'conn_string'),
    pool_size=20, max_overflow=0, pool_recycle=3600, echo=False
)

# engine = create_engine(
#     'mysql+mysqldb://root:grobo14@127.0.0.1/amarak?charset=utf8',
#     pool_size=20, max_overflow=0, pool_recycle=3600, echo=False
# )


from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine,
                       autocommit=False,
                       autoflush=False)
session = scoped_session(Session)
if not database_exists(engine.url):
    create_database(engine.url)
Base.metadata.create_all(engine, checkfirst=True)

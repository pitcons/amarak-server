# encoding: utf-8
import sqlalchemy
from sqlalchemy import or_, and_, distinct
from sqlalchemy.orm import aliased, joinedload, lazyload
from sqlalchemy.orm.exc import NoResultFound
from backends.sqlalchemy_store import *
#from skosprovider_sqlalchemy.providers import SQLAlchemyProvider


class Store(object):

    def __init__(self):
        self.autocommit = True
        self.use_cache = True
        self.term_cache = {}
        self.relation_cache = {}

    def set_autocommit(self, value):
        self.autocommit = value

    def commit(self):
        session.commit()

    def search_by_label(self, label):
        concepts = list(session.query(Concept, ConceptLabel, Scheme)
                        .join(Scheme,
                              Scheme.id==Concept.scheme_id)
                        .join(ConceptLabel,
                              ConceptLabel.concept_id==Concept.id)
                        .filter(or_(ConceptLabel.label==label,
                                    ConceptLabel.label==label.upper(),
                                    ConceptLabel.label==label.capitalize(),
                                ))
                        .all())

        return [
            {'name': concept.name,
             'label': {'lang': label.lang,
                       'type': label.type,
                       'label': label.label},
             'scheme': scheme.name}
            for concept, label, scheme in concepts
        ]

    def search_by_name(self, scheme_name, name, limit=None):
        schemes = self.schemes()
        a_schemes = schemes[scheme_name]['parents'][:] + [scheme_name]
        concepts = (session.query(Concept, Scheme)
                        .join(Scheme,
                              Scheme.id==Concept.scheme_id)
                        .filter(Scheme.name.in_(a_schemes))
                        .filter(Concept.name.like(u'{}%'.format(name))))
        if limit:
            concepts = concepts.limit(limit)

        return [
            {'name': concept.name,
             'scheme': scheme.name}
            for concept, scheme in concepts.all()
        ]

    def schemes(self, name=None):
        by_id = {}

        schemes = {}
        qset = session.query(Scheme)
        if name:
            qset = qset.filter(Scheme.name==name)

        for scheme in qset.all():
            by_id[scheme.id] = scheme.name
            labels = {}
            for label in scheme.labels:
                labels[label.lang] = label.label

            schemes[scheme.name] = {
                "name": scheme.name,
                "name": scheme.name,
                "labels": labels,
                "parents": [
                    s.name for sh, s in
                    (session.query(SchemeHierarchy, Scheme)
                     .join(Scheme,
                           SchemeHierarchy.parent_id==Scheme.id)
                     .filter(SchemeHierarchy.scheme_id==scheme.id)
                     .order_by('weight')
                     .all())
                ],
                "parents_all": [],
                "concept_label_types": {
                    'prefLabel': 'Preferred label',
                    'altLabel': 'Alternative label',
                    'hiddenLabel': 'Hidden label',
                },
                "langs": {
                    'ru': 'Russian',
                    'en': 'English'
                }
            }
        # TODO optimize
        def fill_parents_all(current):
            for parent in schemes[current]['parents']:
                if schemes[parent] in schemes[current]['parents_all']:
                    continue
                schemes[current]['parents_all'] += [parent]
                schemes[current]['parents_all'] += fill_parents_all(parent)

            return schemes[current]['parents_all']

        for scheme in schemes:
            if name:
                all_parents = []
            else:
                all_parents = fill_parents_all(scheme)
            schemes[scheme]['parents_all'] = all_parents
            schemes[scheme]["relations"] = [
                {'id': r.id,
                 'name': r.name,
                 'scheme': r.name}
                for r in self.schemes_relations(
                        [schemes[scheme]['name']] + all_parents)
            ]

        return schemes

    def scheme_get(self, name):
        return session.query(Scheme).filter(
            Scheme.name==name).one()

    def scheme_delete(self, name):
        scheme = self.scheme_get(name)
        (session.query(Scheme)
         .filter(Scheme.id==scheme.id)
         .delete())

    def scheme_update(self, name, data):
        data = data.copy()
        try:
            scheme = self.scheme_get(name)
        except NoResultFound:
            scheme = Scheme(name=name)
            session.add(scheme)

        if 'labels' in data:
            for lang, label in data['labels'].items():
                label_obj = (session.query(SchemeLabel)
                             .filter(SchemeLabel.lang==lang,
                                     SchemeLabel.scheme_id==scheme.id)
                             .first())
                if not label_obj:
                    label_obj = SchemeLabel(lang=lang, scheme_id=scheme.id)

                label_obj.label = label
                session.add(label_obj)

            del data['labels']

        if data:
            for key, value in data.items():
                setattr(scheme, key, value)
            session.add(scheme)

        if self.autocommit:
            session.commit()

    def scheme_add_parent(self, name, parent_name):
        scheme = self.scheme_get(name)
        parent = self.scheme_get(parent_name)

        h = SchemeHierarchy(
            scheme_id=scheme.id,
            parent_id=parent.id,
        )
        session.add(h)
        if self.autocommit:
            session.commit()

    def schemes_relations(self, namees):
        return (session.query(ConceptRelation)
                .filter(ConceptRelation.name.in_(namees))
                .all())

    def scheme_rm_parent(self, name, parent_name):
        scheme = self.scheme_get(name)
        parent = self.scheme_get(parent_name)
        session.query(SchemeHierarchy).filter(
            SchemeHierarchy.scheme_id==scheme.id,
            SchemeHierarchy.parent_id==parent.id,
        ).delete()
        if self.autocommit:
            session.commit()

    def concept_relation_get(self, scheme_name, name):
        scheme = self.scheme_get(scheme_name)
        return session.query(ConceptRelation).filter(
            ConceptRelation.scheme_id==scheme.id,
            ConceptRelation.name==name,
        ).one()

    def concept_all(self, scheme_name, batch=1000):
        scheme_obj = self.scheme_get(scheme_name)
        # for concepts in session.query(Concept).yield_per(batch):
        for concepts in session.query(Concept)\
                               .options(joinedload(Concept.labels))\
                               .filter(Concept.scheme_id==scheme_obj.id)\
                               .all():
                               #.yield_per(batch):
                               #.limit(100):
            yield concepts

    def concept_add_link(self, scheme, relscheme, relname,
                         scheme1, concept1, scheme2, concept2):
        scheme_obj = self.scheme_get(scheme)
        # scheme1_obj = self.scheme_get(scheme1)
        concept1_obj = self.concept_get(concept1)
        # scheme2_obj = self.scheme_get(scheme2)
        concept2_obj = self.concept_get(concept2)
        rel = (session.query(ConceptRelation)
               .filter(ConceptRelation.name==relscheme,
                       ConceptRelation.name==relname).one())
        link = ConceptLink(
            concept1_id=concept1_obj.id,
            concept2_id=concept2_obj.id,
            concept_relation_id=rel.id,
            scheme_id=scheme_obj.id
        )
        session.add(link)
        if self.autocommit:
            session.commit()

    def link_all(self, scheme_name, batch=1000):
        scheme_obj = self.scheme_get(scheme_name)
        # for concepts in session.query(Concept).yield_per(batch):
        for links in session.query(ConceptLink)\
                               .options(joinedload(ConceptLink.relation))\
                               .options(joinedload(ConceptLink.concept1))\
                               .options(joinedload(ConceptLink.concept2))\
                               .filter(ConceptLink.scheme_id==scheme_obj.id)\
                               .all():
                               #.yield_per(batch):
            yield links
        pass

    def concept_rm_link(self, scheme, relscheme, relname,
                        scheme1, concept1, scheme2, concept2):
        scheme_obj = self.scheme_get(scheme)
        # scheme1_obj = self.scheme_get(scheme1)
        concept1_obj = self.concept_get(concept1)
        # scheme2_obj = self.scheme_get(scheme2)
        concept2_obj = self.concept_get(concept2)
        print relscheme, relname
        rel = (session.query(ConceptRelation)
               .filter(ConceptRelation.name==relscheme,
                       ConceptRelation.name==relname).one())
        session.query(ConceptLink).filter(
            ConceptLink.concept1_id==concept1_obj.id,
            ConceptLink.concept2_id==concept2_obj.id,
            ConceptLink.concept_relation_id==rel.id,
            ConceptLink.scheme_id==scheme_obj.id
        ).delete()

        if self.autocommit:
            session.commit()

    def q_top_concepts(self, scheme_name):
        scheme = self.scheme_get(scheme_name)
        rel = self.concept_relation_get('skos', 'broader')

        links = (session.query(ConceptLink.concept1_id)
                 .filter(ConceptLink.concept_relation_id==rel.id))

        concepts = (session.query(Concept, Scheme)
                    .join(Scheme, Scheme.id==Concept.scheme_id)
                    .filter(Concept.scheme_id==scheme.id)
                    .filter(~Concept.id.in_(links)))
        return concepts

    def top_concepts(self, scheme_name):
        schemes = self.schemes()
        stack = [scheme_name]
        visited = set()
        result_q = None
        while stack:

            current = stack.pop(0)
            if result_q:
                result_q = result_q.union(self.q_top_concepts(current))
            else:
                result_q = self.q_top_concepts(current)

            for parent_name in schemes[current]['parents']:
                if parent_name not in visited:
                    visited.add(parent_name)
                    stack.append(parent_name)

        return [{'name': c.name, 'scheme': s.name} for c, s in result_q.all()]

    def concept_update(self, scheme_name, name, data):
        scheme = self.scheme_get(scheme_name)
        print 'scheme', scheme.id, scheme
        try:
            concept = session.query(Concept).filter(
                Concept.scheme_id==scheme.id,
                Concept.name==name).one()
        except NoResultFound:
            concept = Concept(name=name, scheme_id=scheme.id)
            session.add(concept)

        if data:
            if 'name' in data:
                concept.name = data['name']
                session.add(concept)

            if 'labels' in data:

                session.query(ConceptLabel) \
                       .filter(ConceptLabel.concept_id==concept.id)\
                       .delete()

                session.commit()  # TODO hack

                for lang, label_type, title in data['labels']:
                    label_obj = ConceptLabel(
                        concept_id=concept.id,
                        type=label_type,
                        lang=lang,
                        label=title
                    )
                    session.add(label_obj)


            # TODO а что ещёs, кроме labels?
            # for key, value in data.items():
            #     setattr(concept, key, value)
            # session.add(concept)

        if self.autocommit:
            print 'commit', concept.scheme_id, concept
            session.commit()

    def concept_get(self, name):
        return session.query(Concept).filter(
            Concept.name==name).one()

    def concept_delete(self, scheme_name, name):
        scheme = self.scheme_get(scheme_name)
        concept = self.concept_get(name)

        session.query(ConceptLabel).filter(
            ConceptLabel.concept_id==concept.id
        ).delete()
        session.query(ConceptLink).filter(
            or_(ConceptLink.concept1_id==concept.id,
                ConceptLink.concept2_id==concept.id)
        ).delete()
        session.query(Concept).filter(
            Concept.scheme_id==scheme.id,
            Concept.name==name
        ).delete()

        if self.autocommit:
            session.commit()


    def concept_relations(self, scheme_name, concept_name):
        t1 = aliased(Concept, name="t1")
        t2 = aliased(Concept, name="t2")
        s1 = aliased(Scheme, name="s1")
        s2 = aliased(Scheme, name="s2")

        rels = (session.query(ConceptLink, ConceptRelation,
                              t1, t2, Scheme, s1, s2)
                .join(t1, t1.id==ConceptLink.concept1_id)
                .join(t2, t2.id==ConceptLink.concept2_id)
                .join(s1, s1.id==t1.scheme_id)
                .join(s2, s2.id==t2.scheme_id)
                .join(ConceptRelation,
                      ConceptRelation.id==ConceptLink.concept_relation_id)
                .join(Scheme,
                      Scheme.id==ConceptLink.scheme_id)
                .filter(or_(t1.name==concept_name))
                .order_by(ConceptRelation.name, t1.name, t2.name)).all()

        return [
            {'concept1': {'name': t1.name, 'scheme': s1.name},
             'relation': {'name': rel.name},
             'concept2': {'name': t2.name, 'scheme': s2.name},
             'scheme': scheme.name,
             'link': {'id': link.id}}
            for link, rel, t1, t2, scheme, s1, s2 in rels
        ]

    def rm_link(self, link_id):
        session.query(ConceptLink).filter(ConceptLink.id==int(link_id)).delete()
        if self.autocommit:
            session.commit()

    def concept_labels(self, scheme_name, concept_name, flat=False):
        concept = self.concept_get(concept_name)
        labels = (session.query(ConceptLabel)
                  .filter(ConceptLabel.concept_id==concept.id)
                  .order_by('type', 'lang', 'label').all())

        if flat:
            result = [(label.lang, label.type, label.label) for label in labels]
        else:
            result = {}
            for label in labels:
                if label.lang not in result:
                    result[label.lang] = {}
                if label.type not in result[label.lang]:
                    result[label.lang][label.type] = []

                result[label.lang][label.type].append(label.label)

        return result

    def add_concept_label(self, scheme, concept_name, lang, type, label):
        concept = self.concept_get(concept_name)
        label_obj = ConceptLabel(
            concept_id=concept.id,
            type=type,
            lang=lang,
            label=label
        )
        session.add(label_obj)
        if self.autocommit:
            session.commit()

    def rm_concept_label(self, scheme, concept_name, lang, type, label):
        concept = self.concept_get(concept_name)
        session.query(ConceptLabel).filter(
            ConceptLabel.concept_id==concept.id,
            ConceptLabel.lang==lang,
            ConceptLabel.type==type,
            ConceptLabel.label==label
        ).delete()
        if self.autocommit:
            session.commit()

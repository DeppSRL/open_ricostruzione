from django.db import models

class ProgettiManager(models.Manager):

    territorio=None

    def totali(self, territorio=None, territori=None):

        query_set = models.query.QuerySet()

        if territorio:

            if territorio.territorio == territorio.TERRITORIO.R:
                query_set = query_set.filter(territorio_set__cod_reg=territorio.cod_reg)
            elif territorio.territorio == territorio.TERRITORIO.P:
                return self.filter(territorio_set__cod_prov=territorio.cod_prov)
            elif territorio.territorio == territorio.TERRITORIO.C:
                return self.filter(territorio_set__cod_com=territorio.cod_com)
            elif territorio.territorio == territorio.TERRITORIO.N:
                return self.filter(territorio_set__territorio=territorio.TERRITORIO.N)
            elif territorio.territorio == territorio.TERRITORIO.E:
                return self.filter(territorio_set__pk=territorio.pk)
            else:
                raise Exception('Territorio non valido %s' % territorio)

            query_set = query_set.nel_territorio( territorio )
        elif territori:
            query_set = query_set.nei_territori( territori )
#
#        if tipo:
#            query_set = query_set.del_tipo( tipo )
#
#        if tema:
#            query_set = query_set.con_tema( tema )
#
#        if classificazione:
#            query_set = query_set.con_natura( classificazione )
#
#        if soggetto:
#            query_set = query_set.del_soggetto( soggetto )
#
        #        if not query_set:
        #            raise Exception('Richiesta non valida')

        return query_set.distinct()


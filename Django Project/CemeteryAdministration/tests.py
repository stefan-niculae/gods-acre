from django.test import TestCase
from django.core.urlresolvers import reverse
from CemeteryAdministration.models import *
from datetime import date


def revpath(view_name):
    return '{0}:{1}'.format('CemeteryAdministration', view_name)


class RevenueTest(TestCase):
    view_name = 'revenue'

    def setUp(self):
        self.spot1 = Spot.objects.create(parcel='1p',
                                         row='1r',
                                         column='1c')
        self.spot2 = Spot.objects.create(parcel='2p',
                                         row='2r',
                                         column='2c')

    # 0 = same, 1 = different
    # year(on payment), receipt, spot
    # 0 0 0 can't have same year same spot twice #todo
    # 0 0 1
    # 0 1 0 can't have same year same spot twice #todo
    # 0 1 1
    # 1 0 0
    # 1 0 1
    # 1 1 0
    # 1 1 1

    def test1_same_year_same_receipt_different_spots(self):
        receipt1 = ContributionReceipt.objects.create(number=1,
                                                      date=date(2001, 1, 1))
        payment1 = YearlyPayment.objects.create(spot=self.spot1,
                                                receipt=receipt1,
                                                year=2001,
                                                value=100)
        payment2 = YearlyPayment.objects.create(spot=self.spot2,
                                                receipt=receipt1,
                                                year=2001,
                                                value=200)

        response = self.client.get(reverse(revpath(self.view_name)), {'ani': '1'})
        tables = response.context['tables']

        self.assertListEqual(tables[0].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 100, '1/2001'],
                                 [self.spot2.id, '2p', '2r', '2c', 200, '1/2001']
                             ])

    def test2_same_year_different_receipt_different_spots(self):
        receipt2_1 = ContributionReceipt.objects.create(number=1,
                                                        date=date(2002, 1, 1))
        receipt2_2 = ContributionReceipt.objects.create(number=2,
                                                        date=date(2002, 1, 1))
        payment3 = YearlyPayment.objects.create(spot=self.spot1,
                                                receipt=receipt2_1,
                                                year=2002,
                                                value=100)
        payment4 = YearlyPayment.objects.create(spot=self.spot2,
                                                receipt=receipt2_2,
                                                year=2002,
                                                value=200)

        response = self.client.get(reverse(revpath(self.view_name)), {'ani': '2'})
        tables = response.context['tables']

        self.assertListEqual(tables[0].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 100, '1/2002'],
                                 [self.spot2.id, '2p', '2r', '2c', 200, '2/2002']
                             ])

    def test3_different_year_same_receipt_same_spot(self):
        receipt3 = ContributionReceipt.objects.create(number=1,
                                                      date=date(2003, 1, 1))
        payment5 = YearlyPayment.objects.create(spot=self.spot1,
                                                receipt=receipt3,
                                                year=2003,
                                                value=100)
        payment6 = YearlyPayment.objects.create(spot=self.spot1,
                                                receipt=receipt3,
                                                year=1993,
                                                value=200)

        response = self.client.get(reverse(revpath(self.view_name)), {'ani': '3 93'})
        tables = response.context['tables']

        self.assertListEqual(tables[0].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 100, '1/2003']
                             ])
        self.assertListEqual(tables[1].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 200, '1/2003']
                             ])

    def test4_different_year_same_receipt_different_spot(self):
        receipt4 = ContributionReceipt.objects.create(number=1,
                                                      date=date(2004, 1, 1))
        payment5 = YearlyPayment.objects.create(spot=self.spot1,
                                                receipt=receipt4,
                                                year=2004,
                                                value=100)
        payment6 = YearlyPayment.objects.create(spot=self.spot2,
                                                receipt=receipt4,
                                                year=1994,
                                                value=200)
        response = self.client.get(reverse(revpath(self.view_name)), {'ani': '4 94'})
        tables = response.context['tables']

        self.assertListEqual(tables[0].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 100, '1/2004']
                             ])
        self.assertListEqual(tables[1].rows,
                             [
                                 [self.spot2.id, '2p', '2r', '2c', 200, '1/2004']
                             ])

    def test5_different_year_different_receipt_same_spot(self):
        receipt5 = ContributionReceipt.objects.create(number=1,
                                                      date=date(2005, 1, 1))
        receipt6 = ContributionReceipt.objects.create(number=1,
                                                      date=date(1995, 1, 1))
        payment8 = YearlyPayment.objects.create(spot=self.spot1,
                                                receipt=receipt5,
                                                year=2005,
                                                value=100)
        payment9 = YearlyPayment.objects.create(spot=self.spot1,
                                                receipt=receipt6,
                                                year=1995,
                                                value=200)
        response = self.client.get(reverse(revpath(self.view_name)), {'ani': '5 95'})
        tables = response.context['tables']

        self.assertListEqual(tables[0].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 100, '1/2005']
                             ])
        self.assertListEqual(tables[1].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 200, '1/1995']
                             ])

    def test6_different_year_different_receipt_different_spot(self):
        receipt7 = ContributionReceipt.objects.create(number=1,
                                                      date=date(2006, 1, 1))
        receipt8 = ContributionReceipt.objects.create(number=1,
                                                      date=date(1996, 1, 1))
        payment9 = YearlyPayment.objects.create(spot=self.spot1,
                                                receipt=receipt7,
                                                year=2006,
                                                value=100)
        payment10 = YearlyPayment.objects.create(spot=self.spot2,
                                                 receipt=receipt8,
                                                 year=1996,
                                                 value=200)
        response = self.client.get(reverse(revpath(self.view_name)), {'ani': '6 96'})
        tables = response.context['tables']

        self.assertListEqual(tables[0].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 100, '1/2006']
                             ])
        self.assertListEqual(tables[1].rows,
                             [
                                 [self.spot2.id, '2p', '2r', '2c', 200, '1/1996']
                             ])


class OperationsTest(TestCase):
    view_name = 'operations'

    def setUp(self):
        self.spot1 = Spot.objects.create(parcel='1p',
                                         row='1r',
                                         column='1c')
        self.spot2 = Spot.objects.create(parcel='2p',
                                         row='2r',
                                         column='2c')

    def test1_burial_no_note(self):
        operation1 = Operation.objects.create(spot=self.spot1,
                                              date=date(2001, 1, 1),
                                              type='bral',
                                              first_name='a',
                                              last_name='aa')

        response = self.client.get(reverse(revpath(self.view_name)), {'ani': '1'})
        tables = response.context['tables']

        self.assertListEqual(tables[0].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 'a', 'aa', 'înhumare', None],
                             ])

    def test2_exhumation_with_and_without_note(self):
        operation2 = Operation.objects.create(spot=self.spot1,
                                              date=date(2002, 1, 1),
                                              type='exhm',
                                              first_name='b',
                                              last_name='bb')
        operation3 = Operation.objects.create(spot=self.spot2,
                                              date=date(2002, 1, 1),
                                              type='exhm',
                                              first_name='c',
                                              last_name='cc',
                                              note='n')

        response = self.client.get(reverse(revpath(self.view_name)), {'ani': '2'})
        tables = response.context['tables']

        self.assertListEqual(tables[0].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 'b', 'bb', 'dezhumare', None],
                                 [self.spot2.id, '2p', '2r', '2c', 'c', 'cc', 'dezhumare', 'n']
                             ])



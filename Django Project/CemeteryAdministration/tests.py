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
    # 0 0 0 can't have same year same spot twice
    # 0 0 1
    # 0 1 0 can't have same year same spot twice
    # 0 1 1
    # 1 0 0
    # 1 0 1
    # 1 1 0
    # 1 1 1
    # also different deeds
    # also no payment

    def test1_same_year_same_receipt_different_spots(self):
        receipt1 = ContributionReceipt.objects.create(number=1,
                                                      date=date(1901, 1, 1))

        deed1 = OwnershipDeed.objects.create(number=1,
                                             date=date(1991, 1, 1))
        deed1.spots = [self.spot1]

        deed2 = OwnershipDeed.objects.create(number=2,
                                             date=date(2001, 1, 1))
        deed2.spots = [self.spot2]


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
                                 [self.spot1.id, '1p', '1r', '1c', 100, '1/1901'],
                                 [self.spot2.id, '2p', '2r', '2c', 200, '1/1901']
                             ])

    def test2_same_year_different_receipt_different_spots(self):
        receipt2_1 = ContributionReceipt.objects.create(number=1,
                                                        date=date(2002, 1, 1))
        receipt2_2 = ContributionReceipt.objects.create(number=2,
                                                        date=date(2002, 1, 1))
        deed3 = OwnershipDeed.objects.create(number=3,
                                             date=date(2002, 1, 1))
        deed3.spots = [self.spot1, self.spot2]

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
                                                      date=date(1903, 1, 1))

        deed4 = OwnershipDeed.objects.create(number=4,
                                             date=date(1900, 1, 1))
        deed4.spots = [self.spot1]

        payment5 = YearlyPayment.objects.create(spot=self.spot1,
                                                receipt=receipt3,
                                                year=1993,
                                                value=100)
        payment6 = YearlyPayment.objects.create(spot=self.spot1,
                                                receipt=receipt3,
                                                year=2003,
                                                value=200)

        response = self.client.get(reverse(revpath(self.view_name)), {'ani': '93 3'})
        tables = response.context['tables']

        self.assertListEqual(tables[0].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 100, '1/1903']
                             ])
        self.assertListEqual(tables[1].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 200, '1/1903']
                             ])

    def test4_different_year_same_receipt_different_spot(self):
        receipt4 = ContributionReceipt.objects.create(number=1,
                                                      date=date(1904, 1, 1))

        deed5 = OwnershipDeed.objects.create(number=5,
                                             date=date(1900, 1, 1))
        deed5.spots = [self.spot1, self.spot2]


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
                                 [self.spot1.id, '1p', '1r', '1c', 100, '1/1904'],
                                 [self.spot2.id, '2p', '2r', '2c', 0, '-']
                             ])
        self.assertListEqual(tables[1].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 0, '-'],
                                 [self.spot2.id, '2p', '2r', '2c', 200, '1/1904']
                             ])

    def test5_different_year_different_receipt_same_spot(self):
        receipt5 = ContributionReceipt.objects.create(number=1,
                                                      date=date(2005, 1, 1))
        receipt6 = ContributionReceipt.objects.create(number=1,
                                                      date=date(1995, 1, 1))

        deed6 = OwnershipDeed.objects.create(number=6,
                                             date=date(1900, 1, 1))
        deed6.spots = [self.spot1]


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
                                                      date=date(1996, 1, 1))
        receipt8 = ContributionReceipt.objects.create(number=1,
                                                      date=date(2006, 1, 1))

        deed7 = OwnershipDeed.objects.create(number=7,
                                             date=date(1900, 1, 1))
        deed7.spots = [self.spot1]
        deed8 = OwnershipDeed.objects.create(number=8,
                                             date=date(2000, 1, 1))
        deed8.spots = [self.spot2]


        payment9 = YearlyPayment.objects.create(spot=self.spot1,
                                                receipt=receipt7,
                                                year=1996,
                                                value=100)
        payment10 = YearlyPayment.objects.create(spot=self.spot2,
                                                 receipt=receipt8,
                                                 year=2006,
                                                 value=200)
        response = self.client.get(reverse(revpath(self.view_name)), {'ani': '96 6'})
        tables = response.context['tables']

        self.assertListEqual(tables[0].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 100, '1/1996']
                             ])
        self.assertListEqual(tables[1].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 0, '-'],
                                 [self.spot2.id, '2p', '2r', '2c', 200, '1/2006']
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
                                 [self.spot1.id, '1p', '1r', '1c', 'a', 'aa', 'înhumare', 2001, None],
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
                                 [self.spot1.id, '1p', '1r', '1c', 'b', 'bb', 'dezhumare', 2002, None],
                                 [self.spot2.id, '2p', '2r', '2c', 'c', 'cc', 'dezhumare', 2002, 'n']
                             ])


class MaintenanceTest(TestCase):
    view_name = 'maintenance'

    def setUp(self):
        self.spot1 = Spot.objects.create(parcel='1p',
                                         row='1r',
                                         column='1c')
        self.spot2 = Spot.objects.create(parcel='2p',
                                         row='2r',
                                         column='2c')

    # one spot one deed one owner
    # one spot one deed two owners
    # one spot two deeds one owner
    # one spot two deeds (one old one new) two owners
    # two spots one deed one owner
    # two spots one deed two owners
    # two spots two deeds one owner
    # two spots two deeds two owners
    # same year two maintenances
    # owner1: spot1, owner2: spot1 & spot2

    def test1_one_spot_one_deed_one_owner(self):
        maintenance1 = MaintenanceLevel.objects.create(spot=self.spot1,
                                                       year=2001,
                                                       description='ukpt')
        deed1 = OwnershipDeed.objects.create(number=1,
                                             date=date(1991, 1, 1))
        deed1.spots = [self.spot1]

        owner1 = Owner.objects.create(first_name='singur',
                                      last_name='s')
        owner1.ownership_deeds = [deed1]

        response = self.client.get(reverse(revpath(self.view_name)), {'ani': '1'})
        tables = response.context['tables']

        self.assertListEqual(tables[0].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 'singur s', 'neîntreținut'],
                             ])

    def test2_one_spot_one_deed_two_owner(self):
        maintenance2 = MaintenanceLevel.objects.create(spot=self.spot1,
                                                       year=2002,
                                                       description='kept')
        deed2 = OwnershipDeed.objects.create(number=2,
                                             date=date(1992, 1, 1))
        deed2.spots = [self.spot1]

        owner2 = Owner.objects.create(first_name='ana',
                                      last_name='popa')
        owner2.ownership_deeds = [deed2]
        owner3 = Owner.objects.create(first_name='alex',
                                      last_name='popa')
        owner3.ownership_deeds = [deed2]

        response = self.client.get(reverse(revpath(self.view_name)), {'ani': '2'})
        tables = response.context['tables']

        self.assertListEqual(tables[0].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 'alex popa, ana popa', 'întreținut'],
                             ])

    def test3_one_spot_two_deeds_one_owner(self):
        maintenance3 = MaintenanceLevel.objects.create(spot=self.spot1,
                                                       year=2003,
                                                       description='ukpt')
        deed3 = OwnershipDeed.objects.create(number=3,
                                             date=date(1993, 1, 1))
        deed3.spots = [self.spot1]
        deed4 = OwnershipDeed.objects.create(number=4,
                                             date=date(1983, 1, 1))
        deed4.spots = [self.spot1]

        owner4 = Owner.objects.create(first_name='multiple',
                                      last_name='m')
        owner4.ownership_deeds = [deed3, deed4]

        response = self.client.get(reverse(revpath(self.view_name)), {'ani': '3'})
        tables = response.context['tables']

        self.assertListEqual(tables[0].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 'multiple m', 'neîntreținut'],
                             ])

    def test4_one_spot_two_deeds_two_owners(self):
        maintenance4 = MaintenanceLevel.objects.create(spot=self.spot1,
                                                       year=2004,
                                                       description='kept')

        deed5 = OwnershipDeed.objects.create(number=5,
                                             date=date(1994, 1, 24))  # heh
        deed5.spots = [self.spot1]
        deed6 = OwnershipDeed.objects.create(number=6,
                                             date=date(2004, 1, 1))
        deed6.spots = [self.spot1]

        owner5 = Owner.objects.create(first_name='batran',
                                      last_name='a')
        owner5.ownership_deeds = [deed5]
        owner6 = Owner.objects.create(first_name='tanar',
                                      last_name='a')
        owner6.ownership_deeds = [deed6]

        response = self.client.get(reverse(revpath(self.view_name)), {'ani': '4'})
        tables = response.context['tables']

        self.assertListEqual(tables[0].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 'tanar a', 'întreținut'],
                             ])

    def test5_two_spots_one_deed_one_owner(self):
        maintenance5 = MaintenanceLevel.objects.create(spot=self.spot1,
                                                       year=2005,
                                                       description='kept')
        maintenance6 = MaintenanceLevel.objects.create(spot=self.spot2,
                                                       year=2015,
                                                       description='ukpt')

        deed7 = OwnershipDeed.objects.create(number=7,
                                             date=date(1995, 1, 24))  # heh
        deed7.spots = [self.spot1, self.spot2]

        owner7 = Owner.objects.create(first_name='lucky',
                                      last_name='L')
        owner7.ownership_deeds = [deed7]

        response = self.client.get(reverse(revpath(self.view_name)), {'ani': '5 15'})
        tables = response.context['tables']

        self.assertListEqual(tables[0].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 'lucky L', 'întreținut'],
                             ])
        self.assertListEqual(tables[1].rows,
                             [
                                 [self.spot2.id, '2p', '2r', '2c', 'lucky L', 'neîntreținut']
                             ])

    def test6_two_spots_one_deed_two_owners(self):
        maintenance7 = MaintenanceLevel.objects.create(spot=self.spot1,
                                                       year=2006,
                                                       description='kept')
        maintenance8 = MaintenanceLevel.objects.create(spot=self.spot2,
                                                       year=2016,
                                                       description='ukpt')

        deed8 = OwnershipDeed.objects.create(number=8,
                                             date=date(1995, 1, 1))
        deed8.spots = [self.spot1, self.spot2]

        owner8 = Owner.objects.create(first_name='frate',
                                      last_name='f')
        owner8.ownership_deeds = [deed8]
        owner9 = Owner.objects.create(first_name='frate2',
                                      last_name='f')
        owner9.ownership_deeds = [deed8]

        response = self.client.get(reverse(revpath(self.view_name)), {'ani': '6 16'})
        tables = response.context['tables']

        self.assertListEqual(tables[0].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 'frate f, frate2 f', 'întreținut'],
                             ])
        self.assertListEqual(tables[1].rows,
                             [
                                 [self.spot2.id, '2p', '2r', '2c', 'frate f, frate2 f', 'neîntreținut']
                             ])

    def test7_two_spots_two_deeds_one_owner(self):
        maintenance8 = MaintenanceLevel.objects.create(spot=self.spot1,
                                                       year=2007,
                                                       description='kept')
        maintenance9 = MaintenanceLevel.objects.create(spot=self.spot2,
                                                       year=2017,
                                                       description='ukpt')

        deed9 = OwnershipDeed.objects.create(number=9,
                                             date=date(2007, 1, 1))
        deed9.spots = [self.spot1, self.spot2]
        deed10 = OwnershipDeed.objects.create(number=10,
                                              date=date(2007, 2, 1))
        deed10.spots = [self.spot1, self.spot2]

        owner9 = Owner.objects.create(first_name='c',
                                      last_name='cc')
        owner9.ownership_deeds = [deed9, deed10]

        response = self.client.get(reverse(revpath(self.view_name)), {'ani': '7 17'})
        tables = response.context['tables']

        self.assertListEqual(tables[0].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 'c cc', 'întreținut'],
                             ])
        self.assertListEqual(tables[1].rows,
                             [
                                 [self.spot2.id, '2p', '2r', '2c', 'c cc', 'neîntreținut']
                             ])

    def test8_two_spots_two_deeds_two_owners(self):
        maintenance10 = MaintenanceLevel.objects.create(spot=self.spot1,
                                                        year=2008,
                                                        description='kept')
        maintenance11 = MaintenanceLevel.objects.create(spot=self.spot2,
                                                        year=2018,
                                                        description='ukpt')

        deed11 = OwnershipDeed.objects.create(number=11,
                                              date=date(2008, 1, 1))
        deed11.spots = [self.spot1, self.spot2]
        deed12 = OwnershipDeed.objects.create(number=12,
                                              date=date(2008, 2, 1))
        deed12.spots = [self.spot1, self.spot2]

        owner10 = Owner.objects.create(first_name='o1',
                                       last_name='o')
        owner10.ownership_deeds = [deed11, deed12]
        owner11 = Owner.objects.create(first_name='o2',
                                       last_name='o')
        owner11.ownership_deeds = [deed11, deed12]

        response = self.client.get(reverse(revpath(self.view_name)), {'ani': '8 18'})
        tables = response.context['tables']

        self.assertListEqual(tables[0].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 'o1 o, o2 o', 'întreținut'],
                             ])
        self.assertListEqual(tables[1].rows,
                             [
                                 [self.spot2.id, '2p', '2r', '2c', 'o1 o, o2 o', 'neîntreținut']
                             ])

    # can't have same year same spot multiple mainenances

    def test9_same_year_multiple_spots(self):
        maintenance12 = MaintenanceLevel.objects.create(spot=self.spot1,
                                                        year=2009,
                                                        description='ukpt')
        maintenance13 = MaintenanceLevel.objects.create(spot=self.spot2,
                                                        year=2009,
                                                        description='kept')

        deed13 = OwnershipDeed.objects.create(number=13,
                                              date=date(2009, 1, 1))
        deed13.spots = [self.spot1, self.spot2]

        owner12 = Owner.objects.create(first_name='mul',
                                       last_name='m')
        owner12.ownership_deeds = [deed13]

        response = self.client.get(reverse(revpath(self.view_name)), {'ani': '9'})
        tables = response.context['tables']

        self.assertListEqual(tables[0].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 'mul m', 'neîntreținut'],
                                 [self.spot2.id, '2p', '2r', '2c', 'mul m', 'întreținut'],
                             ])

    def test10_interlacing_deeds(self):
        maintenance14 = MaintenanceLevel.objects.create(spot=self.spot1,
                                                        year=2010,
                                                        description='ukpt')
        maintenance15 = MaintenanceLevel.objects.create(spot=self.spot2,
                                                        year=2010,
                                                        description='kept')

        deed14 = OwnershipDeed.objects.create(number=14,
                                              date=date(1910, 1, 1))
        deed14.spots = [self.spot1, self.spot2]

        deed15 = OwnershipDeed.objects.create(number=15,
                                              date=date(2010, 1, 1))
        deed15.spots = [self.spot2]

        owner13 = Owner.objects.create(first_name='old',
                                       last_name='o')
        owner13.ownership_deeds = [deed14]
        owner14 = Owner.objects.create(first_name='new',
                                       last_name='n')
        owner14.ownership_deeds = [deed15]

        response = self.client.get(reverse(revpath(self.view_name)), {'ani': '10'})
        tables = response.context['tables']

        self.assertListEqual(tables[0].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 'old o', 'neîntreținut'],
                                 [self.spot2.id, '2p', '2r', '2c', 'new n', 'întreținut'],
                             ])

    def test11_new_owner(self):
        maintenance16 = MaintenanceLevel.objects.create(spot=self.spot1,
                                                        year=2011,
                                                        description='kept')
        deed16 = OwnershipDeed.objects.create(number=16,
                                              date=date(2111, 1, 1))
        deed16.spots = [self.spot1]

        deed17 = OwnershipDeed.objects.create(number=17,
                                              date=date(2011, 1, 1))
        deed17.spots = [self.spot1]

        owner15 = Owner.objects.create(first_name='viitor',
                                       last_name='v')
        owner15.ownership_deeds = [deed16]
        owner16 = Owner.objects.create(first_name='prezent',
                                       last_name='p')
        owner16.ownership_deeds = [deed17]

        response = self.client.get(reverse(revpath(self.view_name)), {'ani': '11'})
        tables = response.context['tables']

        self.assertListEqual(tables[0].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 'prezent p', 'întreținut']
                             ])


class OwnershipsTest(TestCase):
    view_name = 'ownerships'

    # spots, deeds, receipts, owners
    # 1 1 1 1
    # 1 1 1 2
    # 1 1 2 1
    # 1 1 2 2

    # 1 2 1 1
    # 1 2 1 2
    # 1 2 2 1
    # 1 2 2 2

    # 2 1 1 1
    # 2 1 1 2
    # 2 1 2 1
    # 2 1 2 2

    # 2 2 1 1
    # 2 2 1 2
    # 2 2 2 1
    # 2 2 2 2

    def setUp(self):
        self.spot1 = Spot.objects.create(parcel='1p',
                                         row='1r',
                                         column='1c')
        self.spot2 = Spot.objects.create(parcel='2p',
                                         row='2r',
                                         column='2c')

    def test1_one_of_each(self):
        deed1 = OwnershipDeed.objects.create(number=1,
                                             date=date(2001, 1, 1))
        deed1.spots = [self.spot1]

        owner1 = Owner.objects.create(first_name='ana',
                                      last_name='a')
        owner1.ownership_deeds = [deed1]

        receipt1 = OwnershipReceipt.objects.create(number=1,
                                                   date=date(1901, 1, 1),
                                                   ownership_deed=deed1,
                                                   value=100)

        response = self.client.get(reverse(revpath(self.view_name)), {'ani': '1'})
        tables = response.context['tables']

        self.assertListEqual(tables[0].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 'ana a', '-', '1/2001', '1/1901', ''],
                             ])

    def test2_overriding_deeds(self):
        deed2 = OwnershipDeed.objects.create(number=2,
                                             date=date(2002, 1, 1))
        deed2.spots = [self.spot1, self.spot2]
        deed3 = OwnershipDeed.objects.create(number=3,
                                             date=date(2022, 1, 1))
        deed3.spots = [self.spot1]

        owner1 = Owner.objects.create(first_name='ana',
                                      last_name='a')
        owner1.ownership_deeds = [deed2]
        owner2 = Owner.objects.create(first_name='bob',
                                      last_name='b')
        owner2.ownership_deeds = [deed3]

        receipt1 = OwnershipReceipt.objects.create(number=1,
                                                   date=date(1902, 1, 1),
                                                   ownership_deed=deed2,
                                                   value=100)
        receipt2 = OwnershipReceipt.objects.create(number=2,
                                                   date=date(1922, 1, 1),
                                                   ownership_deed=deed3,
                                                   value=100)

        response = self.client.get(reverse(revpath(self.view_name)), {'ani': '2 22'})
        tables = response.context['tables']

        self.assertListEqual(tables[0].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 'ana a', '-', '2/2002', '1/1902', '#%d P2p R2r C2c' % self.spot2.id],
                                 [self.spot2.id, '2p', '2r', '2c', 'ana a', '-', '2/2002', '1/1902', '#%d P1p R1r C1c' % self.spot1.id],
                             ])
        self.assertListEqual(tables[1].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 'bob b', '-', '3/2022', '2/1922', ''],
                             ])

    def test3_phone_and_two_receipts(self):
        deed4 = OwnershipDeed.objects.create(number=4,
                                             date=date(2003, 1, 1))
        deed4.spots = [self.spot1]

        owner3 = Owner.objects.create(first_name='ana',
                                      last_name='a',
                                      phone='723456789')
        owner3.ownership_deeds = [deed4]
        owner4 = Owner.objects.create(first_name='bob',
                                      last_name='b')
        owner4.ownership_deeds = [deed4]

        receipt3 = OwnershipReceipt.objects.create(number=3,
                                                   date=date(1803, 1, 1),
                                                   ownership_deed=deed4,
                                                   value=100)
        receipt4 = OwnershipReceipt.objects.create(number=4,
                                                   date=date(1903, 1, 1),
                                                   ownership_deed=deed4,
                                                   value=100)

        response = self.client.get(reverse(revpath(self.view_name)), {'ani': '3'})
        tables = response.context['tables']

        self.assertListEqual(tables[0].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 'ana a, bob b', '0723 456 789', '4/2003', '4/1903, 3/1803', ''],
                             ])


class ConstructionsTest(TestCase):
    view_name = 'constructions'

    def setUp(self):
        self.spot1 = Spot.objects.create(parcel='1p',
                                         row='1r',
                                         column='1c')
        self.spot2 = Spot.objects.create(parcel='2p',
                                         row='2r',
                                         column='2c')
        self.spot3 = Spot.objects.create(parcel='3p',
                                         row='3r',
                                         column='3c')

    def test1_one_constr_same_auth_same_spot(self):
        authorization1 = ConstructionAuthorization.objects.create(number=1,
                                                                  date=date(2001, 1, 1))
        authorization1.spots = [self.spot1]

        company1 = ConstructionCompany.objects.create(name='compA')

        construction1 = Construction.objects.create(type='brdr',
                                                    construction_company=company1,
                                                    construction_authorization=authorization1)

        response = self.client.get(reverse(revpath(self.view_name)), {'ani': '1'})
        tables = response.context['tables']

        self.assertListEqual(tables[0].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 'bordură', 'compA', '1/2001', ''],
                             ])

    def test2_two_constr_same_same_auth_same_spot(self):
        authorization2 = ConstructionAuthorization.objects.create(number=2,
                                                                  date=date(2002, 1, 1))
        authorization2.spots = [self.spot1]

        company2 = ConstructionCompany.objects.create(name='compA')

        construction2 = Construction.objects.create(type='brdr',
                                                    construction_company=company2,
                                                    construction_authorization=authorization2)
        construction3 = Construction.objects.create(type='tomb',
                                                    construction_company=company2,
                                                    construction_authorization=authorization2)

        response = self.client.get(reverse(revpath(self.view_name)), {'ani': '2'})
        tables = response.context['tables']

        self.assertListEqual(tables[0].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 'bordură, cavou', 'compA', '2/2002', ''],
                             ])

    def test3_one_constr_one_auth_two_spots(self):
        authorization3 = ConstructionAuthorization.objects.create(number=3,
                                                                  date=date(2003, 1, 1))
        authorization3.spots = [self.spot1, self.spot2]

        company3 = ConstructionCompany.objects.create(name='compA')

        construction4 = Construction.objects.create(type='tomb',
                                                    construction_company=company3,
                                                    construction_authorization=authorization3)

        response = self.client.get(reverse(revpath(self.view_name)), {'ani': '3'})
        tables = response.context['tables']

        self.assertListEqual(tables[0].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 'cavou', 'compA', '3/2003', '#{0} P2p R2r C2c'.format(self.spot2.id)],
                                 [self.spot2.id, '2p', '2r', '2c', 'cavou', 'compA', '3/2003', '#{0} P1p R1r C1c'.format(self.spot1.id)]
                             ])

    def test4_one_constr_one_auth_three_spots(self):
        authorization4 = ConstructionAuthorization.objects.create(number=4,
                                                                  date=date(2004, 1, 1))
        authorization4.spots = [self.spot1, self.spot2, self.spot3]

        company4 = ConstructionCompany.objects.create(name='compA')

        construction5 = Construction.objects.create(type='tomb',
                                                    construction_company=company4,
                                                    construction_authorization=authorization4)

        response = self.client.get(reverse(revpath(self.view_name)), {'ani': '4'})
        tables = response.context['tables']

        self.maxDiff=None
        self.assertListEqual(tables[0].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 'cavou', 'compA', '4/2004', '#{0} P2p R2r C2c, #{1} P3p R3r C3c'.format(self.spot2.id, self.spot3.id)],
                                 [self.spot2.id, '2p', '2r', '2c', 'cavou', 'compA', '4/2004', '#{0} P1p R1r C1c, #{1} P3p R3r C3c'.format(self.spot1.id, self.spot3.id)],
                                 [self.spot3.id, '3p', '3r', '3c', 'cavou', 'compA', '4/2004', '#{0} P1p R1r C1c, #{1} P2p R2r C2c'.format(self.spot1.id, self.spot2.id)],
                             ])

    def test5_two_constructions_one_owner_built_one_firm_built(self):
        authorization5 = ConstructionAuthorization.objects.create(number=5,
                                                                  date=date(2005, 1, 1))
        authorization5.spots = [self.spot1]

        company5 = ConstructionCompany.objects.create(name='compA')

        owner1 = Owner.objects.create(first_name='constructor',
                                      last_name='singur')

        construction6 = Construction.objects.create(type='brdr',
                                                    construction_company=company5,
                                                    construction_authorization=authorization5)
        construction7 = Construction.objects.create(type='tomb',
                                                    owner_builder=owner1,
                                                    construction_authorization=authorization5)

        response = self.client.get(reverse(revpath(self.view_name)), {'ani': '5'})
        tables = response.context['tables']

        self.assertListEqual(tables[0].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 'bordură, cavou', 'compA, constructor singur', '5/2005', ''],
                             ])

    def test6_two_spots_two_constructions_same_auth_same_firm(self):
        authorization6 = ConstructionAuthorization.objects.create(number=6,
                                                                  date=date(2006, 1, 1))
        authorization6.spots = [self.spot1, self.spot2]

        company7 = ConstructionCompany.objects.create(name='compA')

        construction8 = Construction.objects.create(type='brdr',
                                                    construction_company=company7,
                                                    construction_authorization=authorization6)
        construction9 = Construction.objects.create(type='tomb',
                                                    construction_company=company7,
                                                    construction_authorization=authorization6)

        response = self.client.get(reverse(revpath(self.view_name)), {'ani': '6'})
        tables = response.context['tables']

        self.assertListEqual(tables[0].rows,
                             [
                                 [self.spot1.id, '1p', '1r', '1c', 'bordură, cavou', 'compA', '6/2006', '#{0} P2p R2r C2c'.format(self.spot2.id)],
                                 [self.spot2.id, '2p', '2r', '2c', 'bordură, cavou', 'compA', '6/2006', '#{0} P1p R1r C1c'.format(self.spot1.id)]
                             ])
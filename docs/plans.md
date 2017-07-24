## bugs

- [x] constructii: cavou,a1a3,58/12,betojan (row 16) si cavou,a1b3,58/12,betojan (row 17) => in db: doar una din constructii are auth

| rand | tip   | locuri | autorizatii |
| ---- | ----- | ------ | ----------- |
| 1    | cavou | a-1a-1 | 5/15        |
| 2    | cavou | a-1b-1 | 5/15        |

- rand 1: se creeaza o constructie de tip `cavou`, pe locurile `a-1a-1` (unul singur), cu autorizatiile `5/15` (una singura)
  - o autorizatie este data pe o singura constructie (dar o constructie poate avea mai multe autorizatii)
  - o constructie este pe unul sau mai multe locuri (dar un loc poate avea mai multe constructii — cate unul din fiecare tip)
- rand 2: se creeaza o noua constructie, separata de tip `cavou`, pe locurile `a-1b-1` (unul singur) cu autorizatiile `5/15` (una singura)
  - cum autorizatia este pt o singura constructie si pe randul 2 s-a introdus o noua constructie separata inseamna ca autorizatia `5/15` a fost data pt constructia de pe randul 2, "luândui-o" constructiei de pe randul 1
- solutie:
  - a se observa pluralizarea loc**uri** din numele coloanei

| rand | tip   | locuri         | autorizatii |
| ---- | ----- | -------------- | ----------- |
| 1    | cavou | a-1a-1, a-1b-1 | 5/15        |



## behaviour

- ? what happens when "unkept since" > 7 yrs
- an ownership receipt can alternatively be "proces-verbal"





## behind the scenes

1. make sure all unique constraints are entered
2. make sure all models have `Meta#ordering` 
3. add type hints
4. check for unused imports
5. if it impacts performance (too many values): load field autocompletes dynamically http://jet.readthedocs.io/en/latest/autocomplete.html#configuration





## retrieval

1. search for `spot.__str__` not just `.parcel`, `.row` and `.column` (same treatment for other fields as well)
2. apply `RelatedOnlyFieldListFilter` to filters
3. date range filter 

   - https://github.com/tzulberti/django-datefilterspec
4. http://jet.readthedocs.io/en/latest/filters.html#django-admin-rangefilter
5. sort and filter by computed columns
   - eg: last_paid_year for Spot
   - https://stackoverflow.com/questions/991926/custom-filter-in-django-admin-on-django-1-3-or-below
   - total_value for payment receipts
6. make a distinction between operation **type** and construction **type** when filtering spots
   - also "auth number" not just "number" in companies filtering
7. search for "burial" (field choice), not "b" (db value)
   - also kept/unkept (which is a bool)
8. order for computed fields
   - Spot: sharing auth, unkept since, shares deed with
   - companies: #constructions
9. search by month name





## data entry

1. !! clean in `forms.py`
2. handle missing
   - whole nr/year: #pk
   - ?/year: -> #pk/year
3. ! when adding a new payment receipt, make it so you can add select existing units from the inline
4. widget or inline
   - eg: `Spot` has both a field "Payments" where you can select existing `PaymentUnits` and a tab "Payments" where you can create payments only for this spot (or edit existing ones)
5. add buttons for multi select widgets
   - eg: `Spot` has a "Deeds" field (multiselect widget) — you can only select existing deeds, not create new ones
6. warnings
   - any of construction's spots is not among the spots on the authorization
   - more than one deed is active for a spot
   - deed date too far away from receipt date
   - exhumated person is not the same one that is buried (if there is one entered)
   - operation date too far from current
   - there is already a construction on the same spot
   - construction: owner_builder is not one of spots.deeds.owners
   - there is already another receipt for the same payment, and link to it
   - maintenance year too far from current
   - payment unit year: too far away from current year, or ASK how it relates to deed
   - a spot with more than one construction of same type
7. capitalize Ana-Maria and S.R.L properly
8. when the `name` of the `owner` is the one in a "burial" `operation`, suggest to modify the `cancel_reason` on the `deed`
9. show how many there are currently burried when adding a new operation
10. la introducerea unui act nou, pt chitante, numarul default sa fie aceeasi cu cel al actului
11. la introducerea unei chitante noi, valoarea default = suma valorilor stabilite pt toate "platile" pt care este chitanta
12. keep values when pressing 'save and add another'
13. add some admin actions: https://docs.djangoproject.com/en/1.11/ref/contrib/admin/actions/
   - set all kept/unkept?
14. operations: dupa adaugare, cu titlu informativ: pe locul A-1-2 mai sunt inmormantati si: A, B, C
15. upon adding a new deed for a spot, show info with all deeds previously active on each spot
16. warn if dates or years are from far from current day https://docs.djangoproject.com/en/1.11/ref/contrib/admin/#admin-custom-validation
   - warning validation: https://docs.djangoproject.com/en/1.11/ref/contrib/admin/#admin-custom-validation
17. add help_text to model fields
18. ? should every field be editable (`ModelAdmin.list_editable`) in the grid-view, or that is something rarely done and should be saved for the details-view?
    - owner: yes
    - others: ?
19. ? whether the button should say "save and continue editing" or "save as new" `ModelAdmin.save_as`: if duplicating an entity is a frequent task
20. checkboxes for importing to mark each row as solved





## UI

- translation
  - "Deeds", "Constructions", "Authorizations" in spot change, General tab (`verbose_name` in `forms.py`, in `widget=...`?)
    - Owners in Deed change, general tab
  - url paths https://stackoverflow.com/questions/5680405/override-django-admin-urls-for-specific-model
  - js https://docs.djangoproject.com/en/1.11/topics/i18n/translation/#internationalization-in-javascript-code
- semantic coloring:
  - red if `Spot#unkept_since > 7`
  - grey if `Deed#cancel_reason is not None`
- add link from payment units to payment receipts and vice-versa (and for other groupings as well)
- things are not capitalized in romanian: eg [filtrare] "După Chitanță proprietate"
- spacing in import page
- logo
- direct urls `/spot` instead of `/cemetery/spot`
- center things & more styling
- no tabs in change-page, everything one under the other
- change asterisk for required into something more verbose: http://stackoverflow.com/questions/4573355/django-admin-mandatory-fields-with
- ? column order preference
- ? groups order preference. right now it is: (in code structure in models.py & admin.py, fields order in SpotAdmin::list_display, fields order in forms.py, imports)
  - spot
  - ownership
  - operations
  - constructions
  - payments
  - maintenance
- ? payment units & payment receipts repr, table col, filter and search fields





## extra features

- model history: https://django-simple-history.readthedocs.io/en/latest/usage.html
  - add date hierarchy `created at/modified at` to each model: https://docs.djangoproject.com/en/1.11/ref/contrib/admin/#django.contrib.admin.ModelAdmin.date_hierarchy or through `ModelAdmin.ordering`
- make every model annotable?
- some charts?
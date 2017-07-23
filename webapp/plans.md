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

- rework payments into units and receipts
- ? what happens when "unkept since" > 7 yrs
- an ownership receipt can alternatively be "proces-verbal"





## behind the scenes

1. make sure all unique constraints are entered
2. if it impacts performance (too many values): load field autocompletes dynamically http://jet.readthedocs.io/en/latest/autocomplete.html#configuration





## retrieval

1. search for `spot.__str__` not just `.parcel`, `.row` and `.column` (same treatment for other fields as well)

2. apply `RelatedOnlyFieldListFilter` to filters

3. date range filter 

   - https://github.com/tzulberti/django-datefilterspec


- http://jet.readthedocs.io/en/latest/filters.html#django-admin-rangefilter





## data entry

1. handle missing
   - whole nr/year: #pk
   - ?/year: -> #pk/year
2. warn if any of construction's spots is not among the spots on the authorization
3. field validation
   - dates: must be over 1900 and under 2100
   - name: only letters & dashes
   - phone: romanian phone format
4. la introducerea unui act nou, pt chitante, numarul default sa fie aceeasi cu cel al actului
5. la introducerea unei chitante noi, valoarea default = suma valorilor stabilite pt toate "platile" pt care este chitanta
6. keep values when pressing 'save and add another'
7. add some admin actions: https://docs.djangoproject.com/en/1.11/ref/contrib/admin/actions/
   - set all kept/unkept?
8. operations: dupa adaugare, cu titlu informativ: pe locul A-1-2 mai sunt inmormantati si: A, B, C
9. upon adding a new deed for a spot, show info with all deeds previously active on each spot
10. warn if dates or years are from far from current day https://docs.djangoproject.com/en/1.11/ref/contrib/admin/#admin-custom-validation
  - warning validation: https://docs.djangoproject.com/en/1.11/ref/contrib/admin/#admin-custom-validation
11. add help_text to model fields
12. ? should every field be editable (`ModelAdmin.list_editable`) in the grid-view, or that is something rarely done and should be saved for the details-view?
    - owner: yes
    - others: ?
13. ? whether the button should say "save and continue editing" or "save as new" `ModelAdmin.save_as`: if duplicating an entity is a frequent task





## UI

- translation
  - provide `verbose_name` and `verbose_name_plural` for each model field (including foreign fields)
  - `short_description` for model methods
  - `desc` on admin fields
  - urls
- top page instead of "HOME > CEMETERY > OWNERS > Ana" with faded OWNERS, make it "HOME > OWNERS > Ana" with bold colors
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
  - add date hierarchy `created at/modified at` to each model: https://docs.djangoproject.com/en/1.11/ref/contrib/admin/#django.contrib.admin.ModelAdmin.date_hierarchy or through `ModelAdmin.ordering
- make every model annotable?
- some charts?
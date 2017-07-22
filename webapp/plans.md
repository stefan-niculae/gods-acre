# TODO

1. search for `spot.__str__` not just `.parcel`, `.row` and `.column` (same treatment for other fields as well)
2. handle missing nr/year (part of pk)
3. field validation
   - dates: must be over 1900 and under 2100



## consolidation

1. make sure all unique constraints are entered
2. apply `RelatedOnlyFieldListFilter` to filters
3. set `CustomAdminSite` in `urls.py` with `CustomAdminSite.urls` and other places: https://docs.djangoproject.com/en/1.11/ref/contrib/admin/#customizing-the-adminsite-class



## data entry improvements

1. la introducerea unui act nou, pt chitante, numarul default sa fie aceeasi cu cel al actului
2. la introducerea unei chitante noi, valoarea default = suma valorilor stabilite pt toate "platile" pt care este chitanta
3. keep values when pressing 'save and add another'



## more features

- model history: https://django-simple-history.readthedocs.io/en/latest/usage.html
   - add date hierarchy `created at/modified at` to each model: https://docs.djangoproject.com/en/1.11/ref/contrib/admin/#django.contrib.admin.ModelAdmin.date_hierarchy or through `ModelAdmin.ordering`
- add some admin actions: https://docs.djangoproject.com/en/1.11/ref/contrib/admin/actions/
   - set all kept/unkept?
- date range filter https://github.com/tzulberti/django-datefilterspec



## low priority

1. operations: dupa adaugare, cu titlu informativ: pe locul A-1-2 mai sunt inmormantati si: A, B, C
2. upon adding a new deed for a spot, show info with all deeds previously active on each spot
3. warn if dates or years are from far from current day https://docs.djangoproject.com/en/1.11/ref/contrib/admin/#admin-custom-validation
   - warning validation: https://docs.djangoproject.com/en/1.11/ref/contrib/admin/#admin-custom-validation
4. add help_text to model fields
5. no tabs in change-page, everything one under the other
6. change asterisk for required into something more verbose: http://stackoverflow.com/questions/4573355/django-admin-mandatory-fields-with



  ### Maintenance
- add view to enable entering bulk maintenance entities
    - spots: all, multi-select widget for entering parcels to exempt
    - checkmark only for spots with an active deed (default on)
    - enter which year (regex validation, warn if year too far from current)
    - checkmark on whether all should be set to kept or all to unkept (default yes)
    - multi-select widget to enter ones opposite to the default (big list)
- daca este al 7+ ani de neintretinere => este pierdut




# To clarify

-    whether every field should be editable (`ModelAdmin.list_editable`) in the grid-view, or that is something rarely done and should be saved for the details-view
     - owners: yes?
- whether the button should say "save and continue editing" or "save as new" `ModelAdmin.save_as`: if duplicating an entity is a frequent task
  - column order preference
      - eg: always owners last, always spots next to last
  - groups order preference. right now it is: (in code structure in models.py & admin.py, fields order in SpotAdmin::list_display, fields order in forms.py, imports)
      - spot
      - ownership
      - operations
      - constructions
      - payments
      - maintenance
  - what to filter for (eg: by individual spots, or by parcel/row/column?)
     > both
  - este mai greu de facut legatura constructie -> proprietar (si autorizatie -> proprietar)
     - pt ca un loc poate avea un proprietar mai vechi (pe act anulat) si unul curent (pe act activ), iar constructia sa fi fost facuta mai de mult, de vechiul proprietar. acum nu stim de care dintre actele anulate sa legam proprietarii
     - la fel si pt un loc: constructiile aratate vor fi toate. cum pot stii care sunt facute doar pt actul curent?
  - un loc poate avea mai multe constructii?
      > doar de feluri diferite


- semn cand "unkept since" este mai mare de 7 ani







# Iulie

- care sa fie valoarea implicita pt tipul de operatie?

  > acum este inhumare

- nume introduse in forma: Popescu Ana, Ion sunt greu de definit

  - eg: Popescu Ana, Ion, Vasilescu Vasile
  - eg: Popescu Ana Maria, Ion
  - solutie: introducere Popescu Ana, Popescu Ion

- adaugam noi motive de anulare? (pe langa donat, proprietar decedat, pierdut)

  > innoire?

- adaugam un camp nou la Proprietar?

  > localitate?

- comportament asteptat pt intrari duplicate la Proprietari? eg: 

  - Stoian Constantin, Gheorghe Magheru 16
  - Stoian Constantin, Gheorghe Magheru 17
  - solutie: o singura intrare cu Gheorghe Magheru 16-17

- care sa fie valoarea implicita pt tipul unei constructii?

  > acum este nimic
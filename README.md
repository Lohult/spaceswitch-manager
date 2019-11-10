**spaceswitch_manager**

*Space Switch Dialog* is the U.I. for the *spaceswitch_builder* module. The process
is linear.


*  Define a interface transform object.

*  Define an attribute of type "enum". If one doesn't exist on the ui object,
   an enum will be generated.

*  Define a list of spaces.

*  Define the local object.

*  The list of spaces will populate the names of the enum index values.

You have the option to add and remove spaces to the list.
You have the options to skip adding orientations of translations to the Parent
Constraint being used in this system.

Finally, press "Build".

TODO:

* [ ]  Add functionality to update spaces to add or remove orientation and
translation constraints.

* [ ]  Write standalone condition node generator to remove reliance on mgear
framework.

* [ ]  Write space matcher tool to seemlessly switch spaces without "popping"
occuring.

* [ ]  Add function to rename/name spaces to something other than their
transform names.
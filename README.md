# "Carnet du maker" website source code
## By Fabien Batteix (alias Skywodd)

### Overview

This is the source code of the <https://www.carnetdumaker.net/> website.

Made using the Python language and the Django framework.

### Local installation

To run locally, you can do the usual:

1. Create a virtualenv with python 3.4.x binary (and activate it)
2. Install all dependencies:
    ``pip install -r requirements.txt``
3. Alter ``carnetdumaker/settings/*.py`` to reflect your database settings
4. Create the user and database to be used for the project
5. Create all tables using:
    ``./manage.py migrate``
6. Create a super user:
    ``./manage.py createsuperuser``
7. Alter your hosts file to point ``www.carnetdumaker.dev`` to ``127.0.0.1``.
8. Run the server:
    ``./manage.py runserver``
9. Enjoy your local version of "Carnet du maker".

Alternately, you can use the provided Vagrant file to deploy and run a virtual machine for the project.
The provided Vagrant file do not install the requirements.txt, use vagrant ssh to do it manually.
If you're using the bundled provisioning script, the virtualenv is activated upon login.

Remarks: Do not forget to fix the data in the ``sites`` table.
``SITE_ID = 1`` MUST link to the domain ``www.carnetdumaker.dev``, otherwise nothing will work as excepted.

### Copyright policy and derived works

The source code of the project is released under the AGPLv3 license. 

You can do whatever the AGPLv3 license allow you to do, BUT:
- Some vendor files in the ``/static`` directory are under various licenses. Check vendor websites for more information.
- All templates files in the ``/templates`` and media resources (images, logo, etc) are under copyright and **NOT** under the terms of the AGPLv3 license.
- Some templates files include legal information from the TamiaLab organisation. You are **NOT** allowed to use them for any derived works.

Any derived works published under the legal terms of the TamiaLab organisation will be considered as impersonation and immediately taken down.

### Supported browsers

Well, any recent browsers with HTML5 support should work.
Tested in-lab with the latest version of Chrome and Firefox.

The site template make heavy use of the Bootstrap 3.x framework. If your browser is supported by Boostrap, well, all features should work.
For IE versions before 8, upgrade your browser right now, you have no excuse!

### OMG I've found a bug/security breach/mistake/typo in the source code!

Well done! 
Please send us an email through the site, open an issue, or submit a pull request if you're a warrior.

Note: pull requests will not be merged, but instead cloned and commited by the project staff (with a thank comment to the original submitter).
If you want to see your pull request merged, we need a signed copyleft agreement from you.

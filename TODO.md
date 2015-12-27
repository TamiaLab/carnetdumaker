# TODO list for the CarnetDuMaker project

## When possible

- Add more unit-testing on code, especially scenario testing (currently only simple GET requests are tested).
- Add all important apps settings to the main settings files.
- Write text for the remaining two static pages and CGU/CGV.
- Refactor models to remove the fishy "save_without_rendering" method and add a "render_xxx" (default True) kwargs instead.
- Refactor "tools" app into multiples simples apps with unit-tests.

- Set on_delete on ALL foreign key.

## Text rendering engine (PySkCode)

- Add support for cosmetics and smileys in the HTML rendering engine.
- Add tree-nodes sanitation.

## Mailing and notifications

- Create an asynchronous mailer backend using the database as store and a CRON script with a management command for sending emails as batch.
- Create an asynchronous notifications routine using Celery to keep the website responsive and fast.

## Cross publication

- Cross-publish blog articles on ~Twitter~~ / Facebook / Google+.
- Send newsletter by mail for newly blog articles on user demand.
- Cross-publish announcements on ~~Twitter~~ / Facebook / Google+.
- Send newsletter by mail for newly announcements on user demand.

## Blog app

- Add articles bundles feature.
- Add files attachments support for article.
- Handle pub_date modification of article with related forum thread.
- Maybe decouple blog and forum apps by introducing a "go between" app.
- Add "Report mistake" feature for article.
- Add author's articles list and feed.
- Add "use_count" on tag for tag cloud size (SQL driven or field driven?).
- Add "to read" user list feature.
- Maybe add preview key for anonymous preview access.
- Maybe add "hidden" state to article model to allow unreferenced articles.

## Search engine

- Integrate Haystack with ElasticSearch search engine in all apps.
- Add a modification date on all indexed models for fast/optimized index updating.
- Always use the text version of the rendered text instead of the source version to avoid searching skcode/html tags.

## Bug tracker

- Add icons "subscribed", "has post in" and "unread" to all issue tickets in list view.
- Add "edit comment" feature (will also require adding comment revision for legal purposes).
- Add "delete comment" feature. (will require logical deletion with delayed physical deletion for legal purposes).

## Forum app

- Add warning when posting on old topics.
- Add forums/topics reader tracker for stats.
- Add forum post edit history with revisions like for blog articles for legal purposes.
- Add logical deletion with delayed physical deletion for legal purposes.
- Add icons "subscribed", "has post in" and "unread" for all forum threads in list view.
- Add topics/posts per author views and feeds.
- Add forum "unread topics/posts" view.
- Add fields "last_thread", "last_post", "post_count", "thread_count" and "view_count".
- Detect reply during writing (maybe with an hidden form field?).

## Content report app

- Need some refactoring.
- Need more unit-testing.

## File attachements app

- Refactor as "simple to use" form/model fields.
- Add bool flags "require_registration" and "require_membership".
- Use logical deletion with "deleted_at" field instead of physical deletion (will require a management command to cleanup).
- Use secure download with "X-Accel-Redirect" (Apache), "X-Send-File" (Nginx) or "serve()" (DEBUG mode) for serving the file content.
- Add a "download_count" field as en eye-candy.

## Private messages app

- Add file attachments support.

## Registration app

- Add two views to resend the activation key by mail if not send recently.
- Add bool flag "partial match" to username ban model to use ilike instead of iexact for search (use case: ban toto, register later as toto2).

## Snippets app

- Add Snippets directory feature.
- Add license with related feeds and views.
- Add tags with related feeds and views.
- Add bool flags "require_registration" and "require_membership".

## Wish

- Warning/ban user app.
- Internal note system linked with user account.
- Stats app (without requiring cookie).
- Vanity badges app.
- Membership app.
- Shop app.
- Billing app with companion address app.
- Payment app (with SP+ payment gateway support).
- Idea submission with vote app.
- Mini project management app, for articles in progress, with planning and status.
- Form and view to (logicaly) delete own user account (will require some protection like typing the password a second time).
- Contact form app with in-database message backend and notifications.

## API

- Better HTML preview API with per-app (maybe per-user) limitations.
- API check if login JSON callback (to avoid data loose on submit with POST forms).

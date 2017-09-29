define(['marionette', './controller'], function (Marionette, controller) {
    var Router = Marionette.AppRouter.extend({
        'appRoutes': {
            'admin/settings': 'robot',
            'settings': 'robot',
            'admin/settings/node/:name': 'node'
        }
    });

    new Router({controller: controller});
});
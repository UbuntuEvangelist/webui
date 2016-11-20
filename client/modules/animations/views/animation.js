define(['application', './templates/animation.tpl', 'lib/api'],
    function (App, template, api) {
        return Marionette.View.extend({
            template: template,
            tagName: 'span',
            ui: {
                button: '.app-animation'
            },
            events: {
                'click @ui.button': 'buttonClicked'
            },
            modelEvents: {
                change: 'update'
            },
            buttonClicked: function () {
                $('button.app-animation').removeClass('active');
                this.ui.button.addClass('active');

                var name = this.ui.button.data('name');
                Views.trigger('animation_selected', this.model);
                api.playAnimation(name, 25);
            },
            update: function () {
                this.ui.button.text(this.model.get('name'));
            }
        });
    });
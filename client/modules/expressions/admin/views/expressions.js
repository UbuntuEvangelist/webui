define(['application', './expression', './templates/expressions.tpl'],
    function(App, expressionView, template) {
        return Marionette.CompositeView.extend({
            template: template,
            childViewContainer: '.app-expressions',
            childView: expressionView,
            ui: {
                nameField: '.app-expression-name',
                addButton: '.app-create-expression',
                deleteButton: '.app-delete-expression',
                saveButton: '.app-save-expressions'
            },
            events: {
                'keyup @ui.nameField': 'changeExpressionsName',
                'click @ui.addButton': 'addExpressions',
                'click @ui.saveButton': 'updateExpressions',
                'click @ui.deleteButton': 'deleteCurrent'
            },
            initialize: function(options) {
                this.mergeOptions(options, ['motors'])
                this.childViewOptions = {
                    collection: this.motors,
                    expressionsView: this
                }
            },
            onAttach: function() {
                this.ui.deleteButton.attr('disabled', true)
            },
            addExpressions: function() {
                let expression = new Backbone.Model({
                    name: 'NewExpression',
                    motor_positions: this.motors.getRelativePositions()
                })
                this.collection.add(expression)
            },
            updateExpressions: function() {
                let self = this

                this.collection.sync(function() {
                    App.Utilities.showPopover(self.ui.saveButton, 'Saved')
                }, function() {
                    App.Utilities.showPopover(self.ui.saveButton, 'Error saving expressions')
                })
            },
            expressionButtonClicked: function(view) {
                App.trigger('motors:selection:set', true)

                if (this.last_clicked !== view) {
                    this.last_clicked = view
                    this.ui.nameField.val(view.model.get('name'))
                    this.ui.deleteButton.attr('disabled', false)
                }
            },
            changeExpressionsName: function() {
                if (typeof this.last_clicked !== 'undefined')
                    this.last_clicked.model.set('name', this.ui.nameField.val())
            },
            deleteCurrent: function() {
                if (this.last_clicked) {
                    this.last_clicked.model.destroy()
                    this.updateExpressions()
                    this.deselect()
                }
            },
            deselect: function() {
                this.last_clicked = null
                this.ui.deleteButton.attr('disabled', true)
                this.ui.nameField.val('')
            }
        })
    })

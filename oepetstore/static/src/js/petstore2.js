openerp.oepetstore = function(instance, local) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    local.HomePage = instance.Widget.extend({
        className: 'oe_petstore_homepage',
        template: "HomePageTemplate",
        init: function(parent) {
            this._super(parent);
            this.name = "Hansssssss";
        },
        start: function() {
            // // console.log("pet store home page loaded");
            //  this.$el.append("<div>Hello dear Odoo user!</div>");
            //
            //   var greeting = new local.GreetingsWidget(this);
            //     return greeting.appendTo(this.$el);
            // this.$el.append(QWeb.render("HomePageTemplate", {name: "Hans"}));
        },
    });

    instance.web.client_actions.add('petstore.homepage', 'instance.oepetstore.HomePage');
    //
    // local.GreetingsWidget = instance.Widget.extend({
    //     // className: 'oe_petstore_greetings',
    //
    //     // start: function() {
    //     //     this.$el.append("<div>We are so happy to see you again in this menu!</div>");
    //     // },
    //         init: function(parent, name) {
    //         this._super(parent);
    //         this.name = name;
    //     },
    // });
}

(function($) {

  var DEFAULT_JSON_FIELD_SELECTOR = 'textarea';

  /**
   * Construction of EditJSONField
   *
   * @author  fre
   * @since   March 20, 2020
   */
  var App = function(rootEl, config) {

    // config.schema argument is required
    if(!config || !config.schema) {
      console.error("No schema file specified!")
      return;
    }

    this.config     = config || {};
    this.rootEl     = $(rootEl);

    //  Determine the JSON data field
    this.jsonField  = $(this.config.jsonField);
    if(this.jsonField.length == 0)
      this.jsonField = this.rootEl.find(DEFAULT_JSON_FIELD_SELECTOR);

    //  Load the schema
    $.getJSON(this.config.schema)
      .done(this.bind(this._init))
      .fail(function() {
        console.error("Failed to load schema: " + config.schema);
      })

  }


  /**
   * Returns a function that will execute the supplied function in the current context
   *
   * @param {Function} 	fn 			the function to bind
   *
   * @return {function} 	the wrapped function
	 *
	 * @author	fre
	 * @since	March 23, 2020
  */
	App.prototype.bind = function(fn) {
		var context = this;
		return function() {
			return fn.apply(context, arguments);
		}
	}


  //	--------------------------------------------------------------------------------
	//	--------------------------------------------------------------------------------
	//	Private functions
	//	--------------------------------------------------------------------------------
	//	--------------------------------------------------------------------------------

  /**
   * Initialize the EditJSONField
   *
   * @param schema  schema in JSON format to be interpreted
   *
   * @author  fre
   * @since   March 20, 2020
   */
  App.prototype._init = function(schema) {

    this.schema = schema;

    console.log(this.schema);

  }


  window.EditJSONField = App;

})(django.jQuery)

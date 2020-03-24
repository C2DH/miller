(function($) {

  /** Selectors */
  var DEFAULT_JSON_FIELD_SELECTOR = 'textarea';

  /** Attributes */
  var ID = 'id';
  var NAME = 'name';
  var FOR = 'for';

  /** HTML tags */
  var LABEL_TAG = 'label';

  /** HTML */
  var FIELD_CONTAINER_HTML  = '\
    <div class="form-row">\
      <div>\
        <label></label>\
      </div>\
    </div>\
  ';
  var INPUT_FIELD_HTML = '\
    <input type="text" class="vTextField" maxlength="500"></input>\
  ';
  var HELP_TEXT_HTML = '\
    <div class="help"></div>\
  ';


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
    if(this.rootEl.length == 0) {
      console.error("No root element specified!")
      return;
    }

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
    this.field_id_pfx = this.jsonField.attr('id') + '_';

    //  Get JSON data
    this.jsonData = $.parseJSON(this.jsonField.text());

    for(var fieldId in this.schema.properties) {
      this._addField(fieldId, this.schema.properties[fieldId]);
    }

    this._updateJSONData();
  }


  /**
   * Add a field to edit the JSON property identified by the fieldId parameter
   *
   * @param fieldId   id of the json property to edit
   * @param fieldProperties   properties of the json property to edit
   *
   * @author  fre
   * @since   March 24, 2020
   */
  App.prototype._addField = function(fieldId, fieldProperties) {

    this.jsonData[fieldId] = this.jsonData[fieldId] || "";

    //  Add the field container with the label
    var field = $(FIELD_CONTAINER_HTML);
    var label = field.find(LABEL_TAG);
    label
      .attr(FOR, this.field_id_pfx + fieldId)
      .text(fieldProperties.title);

    //  Add the input field
    var inputField = $(INPUT_FIELD_HTML);
    inputField
      .attr(ID, this.field_id_pfx + fieldId)
      .attr(NAME, fieldId)
      .val(this.jsonData[fieldId])
      .insertAfter(label);

    //  Addd the help text
    if(fieldProperties.description)
      $(HELP_TEXT_HTML)
        .text(fieldProperties.description)
        .insertAfter(inputField)

    this.rootEl.append(field);

  }


  /**
   * Update the data on the JSON field
   *
   * @author  fre
   * @since   March 24, 2020
   */
  App.prototype._updateJSONData = function() {
    this.jsonField.text(JSON.stringify(this.jsonData));
  }


  window.EditJSONField = App;

})(django.jQuery)

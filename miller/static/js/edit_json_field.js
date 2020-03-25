(function($) {

  /** Field type */
  var STRING_TYPE = 'string';
  var INTEGER_TYPE = 'integer';
  var BOOLEAN_TYPE = 'boolean';
  var OBJECT_TYPE = 'object';

  /** Selectors */
  var DEFAULT_JSON_FIELD_SELECTOR = 'textarea';

  /** Attributes */
  var ID = 'id';
  var NAME = 'name';
  var FOR = 'for';
  var JSON_DATA = 'json';

  /** HTML tags */
  var LABEL_TAG = 'label';

  /** HTML */
  var FIELDS_CONTAINER_HTML = '\
    <div class="json-fields"></div>\
  ';
  var FIELD_CONTAINER_HTML  = '\
    <div class="form-row">\
      <div>\
        <label></label>\
      </div>\
    </div>\
  ';
  var INPUT_TEXT_FIELD_HTML = '\
    <input type="text" class="vTextField" maxlength="127"></input>\
  ';
  var INPUT_INTEGER_FIELD_HTML = '\
    <input type="text"></input>\
  ';
  var SELECT_FIELD_HTML = '<select></select>';
  var SELECT_OPTION_HTML = '<option></option>';
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


  /**
	 * Custom event implementation  for delegation
	 * Allow to keep the context of the class instance
	 *
	 * @param	type		event type
	 * @param	handler		handler method of the event
	 * @param	el			Object, element, jquery object or selector that matches the element which get the event.
	 * @param	filter		Selector used to filter descendants elements
	 * @param	data		Optional. Data to be passed to the handler
	 *
	 * @author	fre
	 * @since	March 25, 2020
	 */
	App.prototype.delegate = function(type, handler, el, filter, data) {

		$(el).on(type, filter, {context: this, data: data}, function(e) {

			var context 		= e.data.context;

			e.target 			= $(e.target);
			e.delegateTarget 	= $(e.delegateTarget);
			e.currentTarget 	= $(e.currentTarget);
			e.data				= e.data.data;

			handler.apply(context, arguments);
		});
	};


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
    this.jsonData = $.parseJSON(this.jsonField.text()) || {};

    //  Create fields
    var fields = this._addFields(this.schema, this.jsonData);
    this.rootEl.append(fields);

    //  Initialize the event to synchronize fields with the JSON data
    this.delegate('change keyup', this._formField_changeHandler, fields, 'input, select');

    this._updateJSONData();
  }


  /**
   * Add a field to edit the JSON property identified by the fieldId parameter
   *
   * @param schema  Section of the schema which contains the properties of the fields to create
   * @param jsonData  Section of the JSON Data which contains the properties to store the values of the fields to create
   *
   * @return  The jQuery element that matches the container of the new fields

   * @author  fre
   * @since   March 25, 2020
   */
  App.prototype._addFields = function(schema, jsonData) {

    var container = $(FIELDS_CONTAINER_HTML);

    for(var fieldId in schema.properties) {
      container.append(
        this._addField(fieldId, schema.properties[fieldId], jsonData)
      );
    }

    return container;
  }


  /**
   * Add a field to edit the JSON property identified by the fieldId parameter
   *
   * @param fieldId   id of the json property to edit
   * @param fieldProperties   properties from the schema of the field to create
   * @param jsonData  Section of the JSON Data which contains the property to store the value of the field to create
   *
   * @return  The jQuery element that matches the new field

   * @author  fre
   * @since   March 24, 2020
   */
  App.prototype._addField = function(fieldId, fieldProperties, jsonData) {

    jsonData[fieldId] = jsonData[fieldId] || fieldProperties.default;

    //  Add the field container with the label
    var field = $(FIELD_CONTAINER_HTML);
    var label = field.find(LABEL_TAG);
    label
      .attr(FOR, this.field_id_pfx + fieldId)
      .text(fieldProperties.title);

    //  Add the input field
    var formField;
    if(fieldProperties.type == OBJECT_TYPE)
      formField = this._addFields(fieldProperties, jsonData[fieldId]);
    else if(fieldProperties.enum)
      formField = this._addSelectField(fieldId, fieldProperties.enum, jsonData);
    else if(fieldProperties.type == BOOLEAN_TYPE)
      formField = this._addSelectField(fieldId, [false, true], jsonData);
    else
      formField = this._addInputField(fieldId, fieldProperties.type, jsonData);

    formField.insertAfter(label);

    //  Addd the help text
    if(fieldProperties.description)
      $(HELP_TEXT_HTML)
        .text(fieldProperties.description)
        .insertAfter(formField)

    return field;

  }


  /**
   * Add an input field to edit the JSON property identified by the fieldId parameter
   *
   * @param fieldId   id of the json property to edit
   * @param type  type of the property to edit
   * @param jsonData  Section of the JSON Data which contains the property to store the value of the field to create
   *
   * @return  The jQuery element that matches the new field

   * @author  fre
   * @since   March 25, 2020
   */
  App.prototype._addInputField = function(fieldId, type, jsonData) {

    var inputField;
    switch(type) {
    case STRING_TYPE: inputField = $(INPUT_TEXT_FIELD_HTML); break;
    case INTEGER_TYPE: inputField = $(INPUT_INTEGER_FIELD_HTML); break;
    default: inputField = $(INPUT_TEXT_FIELD_HTML);
    }

    inputField
      .attr(ID, this.field_id_pfx + fieldId)
      .attr(NAME, fieldId)
      .val(String(jsonData[fieldId]))
      .data(JSON_DATA, jsonData);

    return inputField;
  }


  /**
   * Add a select field to edit the JSON property identified by the fieldId parameter
   *
   * @param fieldId id of the json property to edit
   * @param options array which contains the list of options for the select field
   * @param value current value of the property
   *
   * @return  The jQuery element that matches the new field

   * @author  fre
   * @since   March 25, 2020
   */
  App.prototype._addSelectField = function(fieldId, options, jsonData) {

    var selectField = $(SELECT_FIELD_HTML);
    for(var i = 0; i < options.length; i++) {
      selectField.append(
        $(SELECT_OPTION_HTML).text(options[i])
      );
    }

    selectField
      .attr(ID, this.field_id_pfx + fieldId)
      .attr(NAME, fieldId)
      .val(String(jsonData[fieldId]))
      .data(JSON_DATA, jsonData);

      return selectField;
  }


  /**
   * Update the data on the JSON field
   *
   * @author  fre
   * @since   March 24, 2020
   */
  App.prototype._updateJSONData = function() {
    this.jsonField.text(JSON.stringify(this.jsonData, null, ' '));
  }


  //	--------------------------------------------------------------------------------
	//	--------------------------------------------------------------------------------
	//	Events
	//	--------------------------------------------------------------------------------
	//	--------------------------------------------------------------------------------

  /**
   * Event dispatched when a input or select field has changed
   *
   * @param	e	object which contains event data
   *
   * @author  fre
   * @since	March 25, 2020
   */
  App.prototype._formField_changeHandler = function(e) {

    var field = e.target;

    field.data(JSON_DATA)[field.attr(NAME)] = field.val();
    this._updateJSONData();
  }


  window.EditJSONField = App;

})(django.jQuery)

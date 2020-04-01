(function($) {

  /** Events */
  var CHANGE_EVENT = 'change';
  var KEY_UP_EVENT = 'keyup';

  /** Field type */
  var STRING_TYPE = 'string';
  var INTEGER_TYPE = 'integer';
  var BOOLEAN_TYPE = 'boolean';
  var OBJECT_TYPE = 'object';

  /** Selectors */
  var DEFAULT_JSON_FIELD_SELECTOR = 'textarea';
  var FORM_ROW_SELECTOR = '.form-row';
  var FIELD_SELECTOR = '.field';
  var ERROR_LIST_SELECTOR = '.errorlist';

  /** Attributes */
  var ID = 'id';
  var NAME = 'name';
  var FOR = 'for';
  var INTEGER = 'integer';
  var READONLY = 'readonly';
  var MAXLENGTH = 'maxlength';
  var JSON_DATA = 'json';
  var OPTIONS_DATA = 'options';
  var PATTERN_DATA = 'pattern';

  /** Classes */
  var REQUIRED = 'required';
  var ERRORS = 'errors';
  var V_LARGE_TEXTFIELD = 'vLargeTextField';

  /** HTML tags */
  var LABEL_TAG = 'label';
  var INPUT_TAG = 'input';
  var SELECT_TAG = 'select';
  var TEXTAREA_TAG = 'textarea';

  /** Messages */
  var ERROR_MESSAGES = {
    required: 'This field is required.',
    options: 'The value is not one of the options.',
    integer: 'The value is not an integer.',
    pattern: 'This value doesi not match the pattern.'
  };

  /** HTML */
  var FIELDS_CONTAINER_HTML = '\
    <div class="json-fields"></div>\
  ';
  var FIELD_CONTAINER_HTML  = '\
    <div class="form-row">\
      <ul class="errorlist"></ul>\
      <div>\
        <label></label>\
      </div>\
    </div>\
  ';
  var TEXTAREA_FIELD_HTML = '\
    <textarea cols="40" rows="10" class="field vLargeTextField"></textarea>\
  ';
  var INPUT_TEXT_FIELD_HTML = '\
    <input type="text" class="field vTextField"></input>\
  ';
  var INPUT_INTEGER_FIELD_HTML = '\
    <input type="text" class="field" integer="integer"></input>\
  ';
  var SELECT_FIELD_HTML = '<select class="field"></select>';
  var SELECT_OPTION_HTML = '<option></option>';
  var HELP_TEXT_HTML = '\
    <div class="help"></div>\
  ';
  var ERROR_LIST_HTML = '<ul class="errorlist"></ul>';
  var LIST_ITEM_HTML = '<li></li>';


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

    //  Default configuration values
    this.config     = {
      validate: false,
      validateOnChange: true
    };
    $.extend(this.config, config);

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


  //	--------------------------------------------------------------------------------
	//	--------------------------------------------------------------------------------
	//	Public functions
	//	--------------------------------------------------------------------------------
	//	--------------------------------------------------------------------------------

  /**
   * Validate all fields
	 *
	 * @author	fre
	 * @since	March 27, 2020
   */
  App.prototype.validateAllFields = function() {

      this.rootEl.find(FIELD_SELECTOR).each(
        this.bind(
          function(i, field) {
            this._validateField($(field));
          }
        )
      );
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

		$(el).on(type, $.isArray(filter) ? filter.join() : filter, {context: this, data: data}, function(e) {

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

    //  Set the json field on read-only
    this.jsonField.attr(READONLY, '');

    //  Create fields
    var fields = this._addFields(this.schema, this.jsonData);
    this.rootEl.append(fields);

    //  Initialize events to synchronize fields with the JSON data
    this.delegate(CHANGE_EVENT, this._formField_changeHandler, fields, FIELD_SELECTOR);
    this.delegate(KEY_UP_EVENT, this._formField_keyUpHandler, fields, [INPUT_TAG, TEXTAREA_TAG]);

    this._updateJSONData();

    if(this.config.validate)
      this.validateAllFields();

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
        this._addField(
          fieldId,
          schema.properties[fieldId],
          jsonData,
          schema.required.indexOf(fieldId) != -1
        )
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
   * @param required  boolean value which determines whether the field is required
   *
   * @return  The jQuery element that matches the new field

   * @author  fre
   * @since   March 24, 2020
   */
  App.prototype._addField = function(fieldId, fieldProperties, jsonData, required) {

    jsonData[fieldId] = jsonData[fieldId] || fieldProperties.default;

    //  Add the field container with the label
    var field = $(FIELD_CONTAINER_HTML);
    var label = field.find(LABEL_TAG);
    label
      .attr(FOR, this.field_id_pfx + fieldId)
      .text(fieldProperties.title);

    if(required)
      label.addClass(REQUIRED);

    //  Add the input field
    var formField;
    if(fieldProperties.type == OBJECT_TYPE)
      formField = this._addFields(fieldProperties, jsonData[fieldId]);
    else if(fieldProperties.enum)
      formField = this._addSelectField(fieldId, fieldProperties.enum, jsonData, required);
    else if(fieldProperties.type == BOOLEAN_TYPE)
      formField = this._addSelectField(fieldId, [String(false), String(true)], jsonData, required);
    else
      formField = this._addInputField(fieldId, fieldProperties.type, jsonData, required, fieldProperties.maxLength)
        .data(PATTERN_DATA, fieldProperties.pattern);

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
   * @param required  boolean value which determines whether the field is required
   *
   * @return  The jQuery element that matches the new field

   * @author  fre
   * @since   March 25, 2020
   */
  App.prototype._addInputField = function(fieldId, type, jsonData, required, maxLength) {

    var inputField;

    //  For string properties without maxLength defined, a textarea is used as input field
    if(!maxLength)
      inputField = $(TEXTAREA_FIELD_HTML);

    else {
      switch(type) {
        case STRING_TYPE: inputField = $(INPUT_TEXT_FIELD_HTML); break;
        case INTEGER_TYPE: inputField = $(INPUT_INTEGER_FIELD_HTML); break;
        default: inputField = $(INPUT_TEXT_FIELD_HTML);
      }
    }

    inputField
      .attr(ID, this.field_id_pfx + fieldId)
      .data(NAME, fieldId)
      .val(String(jsonData[fieldId]))
      .data(JSON_DATA, jsonData);

    //  Set required attribute
    if(required)
      inputField.attr(REQUIRED, '');

    //  Set maxlength attribute
    if(maxLength) {
      inputField.attr(MAXLENGTH, maxLength);
      if(maxLength > 100)
        inputField.addClass(V_LARGE_TEXTFIELD);
    }

    return inputField;
  }


  /**
   * Add a select field to edit the JSON property identified by the fieldId parameter
   *
   * @param fieldId id of the json property to edit
   * @param options array which contains the list of options for the select field
   * @param value current value of the property
   * @param required  boolean value which determines whether the field is required
   *
   * @return  The jQuery element that matches the new field

   * @author  fre
   * @since   March 25, 2020
   */
  App.prototype._addSelectField = function(fieldId, options, jsonData, required) {

    var selectField = $(SELECT_FIELD_HTML);
    for(var i = 0; i < options.length; i++) {
      selectField.append(
        $(SELECT_OPTION_HTML).text(options[i])
      );
    }

    selectField
      .attr(ID, this.field_id_pfx + fieldId)
      .data(NAME, fieldId)
      .val(String(jsonData[fieldId]))
      .data(OPTIONS_DATA, options)
      .data(JSON_DATA, jsonData);

    //  Set required attribute
    if(required)
      selectField.attr(REQUIRED, '');

    return selectField;
  }


  /**
   * Validate the specified field
   *
   * @param field field to Validate
   *
   * @author  fre
   * @since March 26, 2020
   */
  App.prototype._validateField = function(field) {

    var fieldRow = field.parents(FORM_ROW_SELECTOR).first();
    var errorList = fieldRow.children(ERROR_LIST_SELECTOR);
    var value = field.val();

    //  Remove all error messages
    fieldRow.removeClass(ERRORS);
    errorList.empty();

    //  Check required fields
    if(value == '' && field.attr(REQUIRED)) {
      fieldRow.addClass(ERRORS);
      $(LIST_ITEM_HTML)
        .text(ERROR_MESSAGES[REQUIRED])
        .appendTo(errorList);
    }

    //  Check select field with options
    var options = field.data(OPTIONS_DATA);
    if(options && options.indexOf(value) == -1) {
      fieldRow.addClass(ERRORS);
      $(LIST_ITEM_HTML)
        .text(ERROR_MESSAGES[OPTIONS_DATA])
        .appendTo(errorList);
    }

    //  Check integer type
    if(field.attr(INTEGER) && !($.isNumeric(value) && Math.floor(value) == value)) {
      fieldRow.addClass(ERRORS);
      $(LIST_ITEM_HTML)
        .text(ERROR_MESSAGES[INTEGER])
        .appendTo(errorList);
    }

    //  Check pattern (for date field)
    var pattern = field.data(PATTERN_DATA);
    if(pattern && !value.match(pattern)) {
      fieldRow.addClass(ERRORS);
      $(LIST_ITEM_HTML)
        .text(ERROR_MESSAGES[PATTERN_DATA])
        .appendTo(errorList);
    }

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
    var fieldId = field.data(NAME);

    field.data(JSON_DATA)[field.data(NAME)] = field.attr(INTEGER) ? parseInt(field.val()) || 0 : field.val();

    this._updateJSONData();

    if(this.config.validateOnChange)
      this._validateField(field);

}


  /**
   * Event dispatched when a key is released on an input field
   *
   * @param	e	object which contains event data
   *
   * @author  fre
   * @since	March 26, 2020
   */
  App.prototype._formField_keyUpHandler = function(e) {

    var field = e.target;

    field.data(JSON_DATA)[field.data(NAME)] = field.attr(INTEGER) ? parseInt(field.val()) || 0 : field.val();
    this._updateJSONData();
  }


  window.EditJSONField = App;

})(django.jQuery)

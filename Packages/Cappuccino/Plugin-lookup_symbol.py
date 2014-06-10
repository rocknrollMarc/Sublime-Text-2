import re
import subprocess

import sublime
import sublime_plugin


class LookupSymbolCommand(sublime_plugin.TextCommand):
    INGREDIENTS_SEARCH_COMMAND = '''
tell application "Ingredients"
    search front window query "{0}"
    activate
end tell
'''

    DEFAULT_DOC_URL = "http://cappuccino.org/learn/documentation/"

    # A list of the classes in Cappuccino for which doxygen uses an "interface" prefix
    INTERFACE_CLASSES = [
        "_c_p_accordion_view.html",
        "_c_p_alert.html",
        "_c_p_animation.html",
        "_c_p_application.html",
        "_c_p_array.html",
        "_c_p_array_controller.html",
        "_c_p_attributed_string.html",
        "_c_p_base_platform.html",
        "_c_p_base_platform_string.html",
        "_c_p_bezier_path.html",
        "_c_p_binder.html",
        "_c_p_box.html",
        "_c_p_browser.html",
        "_c_p_button.html",
        "_c_p_button_bar.html",
        "_c_p_character_set.html",
        "_c_p_check_box.html",
        "_c_p_cib.html",
        "_c_p_cib_binding_connector.html",
        "_c_p_cib_connector.html",
        "_c_p_cib_control_connector.html",
        "_c_p_cib_outlet_connector.html",
        "_c_p_clip_view.html",
        "_c_p_coder.html",
        "_c_p_collection_view.html",
        "_c_p_collection_view_item.html",
        "_c_p_color.html",
        "_c_p_color_panel.html",
        "_c_p_color_picker.html",
        "_c_p_color_well.html",
        "_c_p_comparison_predicate.html",
        "_c_p_compound_predicate.html",
        "_c_p_control.html",
        "_c_p_controller.html",
        "_c_p_controller_selection_proxy.html",
        "_c_p_cookie.html",
        "_c_p_counted_set.html",
        "_c_p_cursor.html",
        "_c_p_data.html",
        "_c_p_date.html",
        "_c_p_decimal_number.html",
        "_c_p_dictionary.html",
        "_c_p_disclosure_button.html",
        "_c_p_document.html",
        "_c_p_document_controller.html",
        "_c_p_drag_server.html",
        "_c_p_dragging_info.html",
        "_c_p_enumerator.html",
        "_c_p_event.html",
        "_c_p_exception.html",
        "_c_p_expression.html",
        "_c_p_expression__aggregate.html",
        "_c_p_expression__constant.html",
        "_c_p_expression__function.html",
        "_c_p_expression__keypath.html",
        "_c_p_expression__self.html",
        "_c_p_expression__set.html",
        "_c_p_expression__subquery.html",
        "_c_p_expression__variable.html",
        "_c_p_flash_movie.html",
        "_c_p_flash_view.html",
        "_c_p_font.html",
        "_c_p_font_manager.html",
        "_c_p_formatter.html",
        "_c_p_function_operation.html",
        "_c_p_graphics_context.html",
        "_c_p_h_t_t_p_u_r_l_response.html",
        "_c_p_image.html",
        "_c_p_image_view.html",
        "_c_p_index_path.html",
        "_c_p_invocation.html",
        "_c_p_invocation_operation.html",
        "_c_p_is_nil_transformer.html",
        "_c_p_is_not_nil_transformer.html",
        "_c_p_j_s_o_n_p_connection.html",
        "_c_p_key_binding.html",
        "_c_p_keyed_archiver.html",
        "_c_p_keyed_unarchiver.html",
        "_c_p_level_indicator.html",
        "_c_p_menu.html",
        "_c_p_menu_item.html",
        "_c_p_mutable_array.html",
        "_c_p_mutable_set.html",
        "_c_p_negate_boolean_transformer.html",
        "_c_p_notification.html",
        "_c_p_notification_center.html",
        "_c_p_number.html",
        "_c_p_number_formatter.html",
        "_c_p_object_controller.html",
        "_c_p_open_panel.html",
        "_c_p_operation.html",
        "_c_p_operation_queue.html",
        "_c_p_outline_view.html",
        "_c_p_panel.html",
        "_c_p_pasteboard.html",
        "_c_p_platform.html",
        "_c_p_platform_string.html",
        "_c_p_platform_window.html",
        "_c_p_pop_up_button.html",
        "_c_p_popover.html",
        "_c_p_predicate.html",
        "_c_p_predicate_editor.html",
        "_c_p_predicate_editor_row_template.html",
        "_c_p_predicate_scanner.html",
        "_c_p_progress_indicator.html",
        "_c_p_property_list_serialization.html",
        "_c_p_proxy.html",
        "_c_p_radio.html",
        "_c_p_responder.html",
        "_c_p_rule_editor.html",
        "_c_p_run_loop.html",
        "_c_p_save_panel.html",
        "_c_p_scanner.html",
        "_c_p_screen.html",
        "_c_p_scroll_view.html",
        "_c_p_scroller.html",
        "_c_p_search_field.html",
        "_c_p_secure_text_field.html",
        "_c_p_segmented_control.html",
        "_c_p_shadow.html",
        "_c_p_shadow_view.html",
        "_c_p_slider.html",
        "_c_p_slider_color_picker.html",
        "_c_p_sort_descriptor.html",
        "_c_p_sound.html",
        "_c_p_split_view.html",
        "_c_p_stepper.html",
        "_c_p_tab_view.html",
        "_c_p_tab_view_item.html",
        "_c_p_table_column.html",
        "_c_p_table_header_view.html",
        "_c_p_table_view.html",
        "_c_p_text_field.html",
        "_c_p_theme.html",
        "_c_p_theme_blend.html",
        "_c_p_timer.html",
        "_c_p_token_field.html",
        "_c_p_toolbar.html",
        "_c_p_toolbar_item.html",
        "_c_p_tree_node.html",
        "_c_p_u_r_l.html",
        "_c_p_u_r_l_connection.html",
        "_c_p_u_r_l_request.html",
        "_c_p_u_r_l_response.html",
        "_c_p_unarchive_from_data_transformer.html",
        "_c_p_undo_manager.html",
        "_c_p_user_defaults.html",
        "_c_p_user_defaults_controller.html",
        "_c_p_user_session_manager.html",
        "_c_p_value.html",
        "_c_p_value_transformer.html",
        "_c_p_view.html",
        "_c_p_view_animation.html",
        "_c_p_view_controller.html",
        "_c_p_web_d_a_v_manager.html",
        "_c_p_web_script_object.html",
        "_c_p_web_view.html",
        "_c_p_window_controller.html"
    ]

    # A list of the classes in Cappuccino for which doxygen uses a "class" prefix
    CLASS_CLASSES = [
        "_c_p_accordion_view_item.html",
        "_c_p_bundle.html",
        "_c_p_color_wheel_color_picker.html",
        "_c_p_decimal_number_handler.html",
        "_c_p_index_set.html",
        "_c_p_mutable_attributed_string.html",
        "_c_p_mutable_dictionary.html",
        "_c_p_mutable_index_set.html",
        "_c_p_nine_part_image.html",
        "_c_p_null.html",
        "_c_p_object.html",
        "_c_p_predicate___b_o_o_l.html",
        "_c_p_predicate_utilities.html",
        "_c_p_radio_group.html",
        "_c_p_set.html",
        "_c_p_string.html",
        "_c_p_table_column_value_binder.html",
        "_c_p_three_part_image.html",
        "_c_p_user_defaults_cookie_store.html",
        "_c_p_user_defaults_local_store.html",
        "_c_p_user_defaults_store.html",
        "_c_p_window.html"
    ]

    def __init__(self, view):
        super(LookupSymbolCommand, self).__init__(view)
        self.searchHandlers = {
            "ingredients": self.lookupInIngredients,
            "web": self.lookupInCappuccinoDocs
        }
        self.scopes = []

    def is_enabled(self):
        return sublime.platform() == "osx" and self.view.settings().get("syntax").endswith("/Objective-J.tmLanguage")

    def run(self, edit, target=None):
        if not target:
            target = self.view.settings().get("cappuccino_lookup_target")

            if not target:
                sublime.error_message("No target application has been set for symbol lookups.")
                return

        msg = self.lookup(target)

        if msg:
            sublime.error_message(msg)

    def lookup(self, target):
        region = self.view.sel()[0]
        region = sublime.Region(region.a, region.b)
        wordRegion = self.view.word(region)
        word = self.view.substr(wordRegion)

        # If the region is empty (a cursor) and is to the right of a non-empty word,
        # move it one character to the left so that the scope is the scope of the word.
        if region.empty() and word and region.begin() == wordRegion.end():
            region = sublime.Region(region.a - 1, region.a - 1)

        line = self.view.substr(self.view.line(region))
        self.scopes = self.view.scope_name(region.begin()).split()
        searchText = ""

        if word.startswith("CP"):
            searchText = word

        elif "meta.implementation.declaration.js.objj" in self.scopes:
            searchText, error = self.getClassNameFromImplementation(line)

            if error is not None:
                return error

        elif "meta.method.js.objj" in self.scopes:
            matches = re.findall(r'(?:^[-+]\s*\(\w+\)(\w+:?))|(\w+:)', line)

            if len(matches):
                if len(matches) == 1:
                    searchText = ''.join(matches[0])
                else:
                    searchText = reduce(lambda x, y: ''.join(x) + ''.join(y), matches)

        elif "source.js.objj" in self.scopes:
            searchText = self.view.substr(self.view.word(region))

        else:
            return "You are not within Objective-J source."

        return self.searchHandlers[target](searchText)

    def getClassNameFromImplementation(self, line):
        matches = re.match(r'@implementation\s+(\w+)(?:\s:\s+(\w+))?', line)

        if matches:
            className = matches.group(1)
            superclassName = matches.group(2)

            if className.startswith("CP"):
                return (className, None)
            elif superclassName.startswith("CP"):
                return (superclassName, None)
            else:
                return (None, "Neither class is a Cappuccino class, no documentation is available.")
        else:
            return (None, "This is not a well-formed class declaration.")

    def lookupInIngredients(self, searchText):
        if not searchText:
            return "You are not within a symbol."

        process = subprocess.Popen(["/usr/bin/osascript"], stdin=subprocess.PIPE)

        if process:
            searchText = re.sub(r"\bCP(?=\w+)", "NS", searchText).replace("Cib", "Nib")
            process.communicate(input=self.INGREDIENTS_SEARCH_COMMAND.format(searchText))
            process.stdin.close()

    def lookupInCappuccinoDocs(self, searchText):
        """
        Open the documentation related to given text
        @type searchText: String
        @param searchText: The text to search in documentation
        """

        # We can only lookup classes in the Cappuccino docs, so if we have
        # something other than what looks like a class, try to find the closest
        # enclosing @implementation.
        if not searchText.startswith("CP") or "support.constant.cappuccino" in self.scopes:
            regions = self.view.find_by_selector("meta.implementation.js.objj")
            implementationRegion = None
            point = self.view.sel()[0]

            for region in regions:
                if region.contains(point):
                    implementationRegion = region
                    break

            if implementationRegion is not None:
                line = self.view.substr(self.view.line(implementationRegion.begin()))
                searchText, error = self.getClassNameFromImplementation(line)

                if error is not None:
                    return error
            else:
                return '"{0}" is not a class or within a class.'.format(searchText)

        def replacer(matchObj):
            return "_" + matchObj.group(0).lower()

        pageName = re.sub(r"([A-Z])", replacer, searchText) + ".html"
        baseUrl = self.view.settings().get("cappuccino_doc_base_url", self.DEFAULT_DOC_URL)

        # Ensure the base url ends with '/'
        if baseUrl[-1] != "/":
            baseUrl = baseUrl + "/"

        # Some classes in Cappuccino docs are prefixed with
        # "interface_", some with "class_". So we have to try multiple prefixes.
        if not self.openCappuccinoDoc(baseUrl, pageName):
            return 'No documentation is available for "{0}" or its enclosing class.'.format(searchText)

    def openCappuccinoDoc(self, baseUrl, pageName):
        try:
            if pageName in self.INTERFACE_CLASSES:
                prefix = "interface"
            elif pageName in self.CLASS_CLASSES:
                prefix = "class"
            else:
                return False

            url = "{0}{1}{2}".format(baseUrl, prefix, pageName)
            subprocess.call(['open', url], shell=False)
            return True
        except:
            return False

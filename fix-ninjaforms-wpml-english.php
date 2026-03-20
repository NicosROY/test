<?php
/**
 * Plugin Name: Fix Ninja Forms WPML English Translation
 * Description: Forces Ninja Forms to display translated fields when WPML switches to English. Drop this file into wp-content/mu-plugins/.
 * Version: 1.0.0
 * Author: Hotfix
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

/**
 * Only bootstrap when both Ninja Forms and WPML are active.
 */
add_action( 'plugins_loaded', function () {

    if ( ! class_exists( 'Ninja_Forms' ) ) {
        return;
    }
    if ( ! defined( 'ICL_SITEPRESS_VERSION' ) && ! function_exists( 'icl_get_languages' ) ) {
        return;
    }

    add_filter( 'ninja_forms_display_fields',        'nf_wpml_en_translate_fields', 9999 );
    add_filter( 'ninja_forms_display_form_settings',  'nf_wpml_en_translate_form_settings', 9999 );

    add_filter( 'ninja_forms_localize_fields',        'nf_wpml_en_translate_fields', 9999 );
    add_filter( 'ninja_forms_localize_form_settings',  'nf_wpml_en_translate_form_settings', 9999 );
}, 99 );

/**
 * Return the WPML default language code, cached per request.
 */
function nf_wpml_en_get_default_lang() {
    static $default = null;
    if ( $default === null ) {
        $default = apply_filters( 'wpml_default_language', '' );
    }
    return $default;
}

/**
 * Return the WPML current language code, cached per request.
 */
function nf_wpml_en_get_current_lang() {
    static $current = null;
    if ( $current === null ) {
        $current = apply_filters( 'wpml_current_language', '' );
    }
    return $current;
}

/**
 * Translate a single string through WPML String Translation.
 *
 * Tries the standard ST domain first (`ninja-forms-<form_id>`), then the
 * legacy domain (`ninja_forms`), then falls back to the generic domain.
 */
function nf_wpml_en_translate_string( $value, $name, $form_id = 0 ) {
    if ( empty( $value ) || ! is_string( $value ) ) {
        return $value;
    }

    $domains = array();
    if ( $form_id ) {
        $domains[] = 'ninja-forms-' . $form_id;
        $domains[] = 'ninja_forms_form_' . $form_id;
    }
    $domains[] = 'ninja_forms';
    $domains[] = 'ninja-forms';
    $domains[] = 'Ninja Forms';

    foreach ( $domains as $domain ) {
        $translated = apply_filters( 'wpml_translate_string', $value, $name, array(
            'domain' => $domain,
        ) );
        if ( $translated !== $value ) {
            return $translated;
        }
    }

    return $value;
}

/**
 * Walk every field and apply WPML string translations for translatable keys.
 */
function nf_wpml_en_translate_fields( $fields ) {
    $current = nf_wpml_en_get_current_lang();
    $default = nf_wpml_en_get_default_lang();

    if ( ! $current || $current === $default ) {
        return $fields;
    }

    $translatable_keys = array(
        'label',
        'placeholder',
        'default',
        'help_text',
        'desc_text',
        'element_class',
        'submit_text',
        'value',
        'link_text',
        'custom_name_attribute',
    );

    $html_keys = array(
        'default',
        'value',
    );

    foreach ( $fields as &$field ) {
        $settings = isset( $field['settings'] ) ? $field['settings'] : $field;
        $is_nested = isset( $field['settings'] );

        $form_id = 0;
        if ( isset( $settings['form_id'] ) ) {
            $form_id = (int) $settings['form_id'];
        } elseif ( isset( $settings['formID'] ) ) {
            $form_id = (int) $settings['formID'];
        }

        $field_id  = isset( $settings['id'] )  ? $settings['id']  : ( isset( $settings['key'] ) ? $settings['key'] : '' );
        $field_key = isset( $settings['key'] )  ? $settings['key'] : '';
        $field_type = isset( $settings['type'] ) ? $settings['type'] : '';

        foreach ( $translatable_keys as $key ) {
            $val = $is_nested
                ? ( isset( $field['settings'][ $key ] ) ? $field['settings'][ $key ] : null )
                : ( isset( $field[ $key ] ) ? $field[ $key ] : null );

            if ( empty( $val ) || ! is_string( $val ) ) {
                continue;
            }

            $names = nf_wpml_en_build_string_names( $key, $field_id, $field_key, $form_id );
            $translated = $val;

            foreach ( $names as $name ) {
                $try = nf_wpml_en_translate_string( $val, $name, $form_id );
                if ( $try !== $val ) {
                    $translated = $try;
                    break;
                }
            }

            if ( $translated !== $val ) {
                if ( $is_nested ) {
                    $field['settings'][ $key ] = $translated;
                } else {
                    $field[ $key ] = $translated;
                }
            }
        }

        if ( $field_type === 'html' ) {
            $html_val = $is_nested
                ? ( isset( $field['settings']['default'] ) ? $field['settings']['default'] : '' )
                : ( isset( $field['default'] ) ? $field['default'] : '' );

            if ( ! empty( $html_val ) && is_string( $html_val ) ) {
                $names = nf_wpml_en_build_string_names( 'default', $field_id, $field_key, $form_id );
                foreach ( $names as $name ) {
                    $try = nf_wpml_en_translate_string( $html_val, $name, $form_id );
                    if ( $try !== $html_val ) {
                        if ( $is_nested ) {
                            $field['settings']['default'] = $try;
                        } else {
                            $field['default'] = $try;
                        }
                        break;
                    }
                }
            }
        }

        if ( isset( $settings['options'] ) && is_array( $settings['options'] ) ) {
            foreach ( $settings['options'] as $opt_idx => &$option ) {
                $opt_label = isset( $option['label'] ) ? $option['label'] : '';
                $opt_value = isset( $option['value'] ) ? $option['value'] : '';

                if ( ! empty( $opt_label ) ) {
                    $names = nf_wpml_en_build_option_names( 'label', $field_id, $field_key, $opt_idx, $form_id );
                    foreach ( $names as $name ) {
                        $try = nf_wpml_en_translate_string( $opt_label, $name, $form_id );
                        if ( $try !== $opt_label ) {
                            $option['label'] = $try;
                            break;
                        }
                    }
                }

                if ( ! empty( $opt_value ) && is_string( $opt_value ) ) {
                    $names = nf_wpml_en_build_option_names( 'value', $field_id, $field_key, $opt_idx, $form_id );
                    foreach ( $names as $name ) {
                        $try = nf_wpml_en_translate_string( $opt_value, $name, $form_id );
                        if ( $try !== $opt_value ) {
                            $option['value'] = $try;
                            break;
                        }
                    }
                }
            }
            unset( $option );

            if ( $is_nested ) {
                $field['settings']['options'] = $settings['options'];
            } else {
                $field['options'] = $settings['options'];
            }
        }
    }
    unset( $field );

    return $fields;
}

/**
 * Translate form-level settings (title, success message, etc.).
 */
function nf_wpml_en_translate_form_settings( $settings ) {
    $current = nf_wpml_en_get_current_lang();
    $default = nf_wpml_en_get_default_lang();

    if ( ! $current || $current === $default ) {
        return $settings;
    }

    $form_id = isset( $settings['id'] ) ? (int) $settings['id'] : 0;

    $form_keys = array(
        'title',
        'success_msg',
        'changeDateErrorMsg',
        'confirmFieldErrorMsg',
        'fieldTextareaRTEInsertLink',
        'fieldTextareaRTEInsertMedia',
        'fieldTextareaRTESelectAFile',
        'formErrorsCorrectErrors',
        'honeypotHoneypotError',
        'validateRequiredField',
    );

    foreach ( $form_keys as $key ) {
        if ( empty( $settings[ $key ] ) || ! is_string( $settings[ $key ] ) ) {
            continue;
        }

        $val   = $settings[ $key ];
        $names = array(
            "form_{$form_id}_{$key}",
            "{$key}_{$form_id}",
            $key,
        );

        foreach ( $names as $name ) {
            $try = nf_wpml_en_translate_string( $val, $name, $form_id );
            if ( $try !== $val ) {
                $settings[ $key ] = $try;
                break;
            }
        }
    }

    return $settings;
}

/**
 * Build an array of possible WPML string names for a given field property.
 */
function nf_wpml_en_build_string_names( $key, $field_id, $field_key, $form_id ) {
    $names = array();

    if ( $field_id ) {
        $names[] = "{$key}_{$field_id}";
        $names[] = "field_{$field_id}_{$key}";
        $names[] = "{$field_id}_{$key}";
    }
    if ( $field_key ) {
        $names[] = "{$key}_{$field_key}";
        $names[] = "field_{$field_key}_{$key}";
    }
    if ( $form_id && $field_id ) {
        $names[] = "form_{$form_id}_field_{$field_id}_{$key}";
    }
    $names[] = $key;

    return $names;
}

/**
 * Build possible WPML string names for a field option (select / radio / checkbox).
 */
function nf_wpml_en_build_option_names( $prop, $field_id, $field_key, $opt_index, $form_id ) {
    $names = array();

    if ( $field_id ) {
        $names[] = "field_{$field_id}_option_{$opt_index}_{$prop}";
        $names[] = "{$prop}_{$field_id}_{$opt_index}";
    }
    if ( $field_key ) {
        $names[] = "field_{$field_key}_option_{$opt_index}_{$prop}";
    }
    if ( $form_id && $field_id ) {
        $names[] = "form_{$form_id}_field_{$field_id}_option_{$opt_index}_{$prop}";
    }

    return $names;
}

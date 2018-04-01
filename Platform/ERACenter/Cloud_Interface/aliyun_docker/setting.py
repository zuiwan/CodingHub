#!/usr/bin/env python
# -*- coding: utf-8 -*-

JUPYTER_CSS = '''body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, HelveticaNeue, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol';
}

pre, code {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Monaco, Courier, monospace;
}

.container {
  width: 100%;
  max-width: 1040px;
  padding: 0 20px;
}

#header-container {
  display: none !important;
}

.navbar-default {
  border-color: #f1f4f9;
  background: none;
}

.btn-default {
  color: #5f7e9c;
}

.dropdown:hover {
  background-color: #f1f4f9;
}

.dropdown:active {
  background-color: #eff6ff;
}

.dropdown a {
  color: #5f7e9c;
}

.dropdown a:hover {
  color: #2991ff;
}

.btn-default {
  border-color: #e0e5ea;
}

.btn-default:hover {
  background-color: #f1f4f9;
  color: #2991ff;
  border-color: #2991ff;
}

.btn-default:active, .btn-default:focus {
  background-color: #eff6ff;
  color: #1581f3;
  border-color: #1581f3;
}

#notebook {
  background-color: white;
}

#maintoolbar-container {
  padding: 0;
}

#notebook-container {
  box-shadow: none;
}

div.cell.selected, div.cell.selected.jupyter-soft-selected {
  border-color: #e0e5ea;
}

div.cell.selected:before,
div.cell.selected.jupyter-soft-selected:before {
  background: #2991ff;
}

div.input_area {
  background-color: #f6f9fd;
  border-color: #e0e5ea;
}

div.input_prompt {
  color: #2991ff;
}

div.output_prompt {
  color: #62c48b;
}

.edit_mode div.cell.selected {
  border-color: #62c48b;
}

.edit_mode div.cell.selected:before {
  background: #62c48b;
}

.CodeMirror, div.output_area pre {
  color: #354e7b;
}

.CodeMirror {
  font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, Monaco, Courier, monospace;
  height: auto;
  color: #2c4779;
  font-size: 13px;
  line-height: 20px;
  border: 1px solid #f1f4f9;
  border-radius: 5px
}

.CodeMirror-lines {
  padding: 5px 0
}

.CodeMirror pre {
  padding: 0 10px
}

.CodeMirror-gutter-filler,
.CodeMirror-scrollbar-filler {
  background-color: #fff
}

.CodeMirror-gutters {
  border-right: 1px solid #f1f4f9;
  background-color: #f9fcff;
  white-space: nowrap
}

.CodeMirror-linenumber {
  padding: 0 5px;
  min-width: 30px;
  text-align: right;
  color: #9aaec1;
  white-space: nowrap
}

.CodeMirror-guttermarker {
  color: #354e7b
}

.CodeMirror-guttermarker-subtle {
  color: #9aaec1
}

.CodeMirror-cursor {
  border-left: 2px solid #2991ff;
  border-right: none;
  width: 0
}

.CodeMirror div.CodeMirror-secondarycursor {
  border-left: 2px solid #57a9ff
}

.cm-tab {
  display: inline-block;
  text-decoration: inherit
}

.CodeMirror-rulers {
  position: absolute;
  left: 0;
  right: 0;
  top: -50px;
  bottom: -20px;
  overflow: hidden
}

.CodeMirror-ruler {
  border-left: 1px solid #e0e5ea;
  top: 0;
  bottom: 0;
  position: absolute
}

.cm-s-default .cm-header {
  color: #2991ff
}

.cm-s-default .cm-quote {
  color: #29a634
}

.cm-negative {
  color: #f33f12
}

.cm-positive {
  color: #29a634
}

.cm-header,
.cm-strong {
  font-weight: 700
}

.cm-em {
  font-style: italic
}

.cm-link {
  text-decoration: underline
}

.cm-strikethrough {
  text-decoration: line-through
}

.cm-s-default .cm-keyword {
  color: #e36209
}

.cm-s-default .cm-atom {
  color: #c74454
}

.cm-s-default .cm-number {
  color: #0068d6
}

.cm-s-default .cm-def {
  color: #6f42c1
}

.cm-s-default .cm-variable-2 {
  color: #7157d9
}

.cm-s-default .cm-type,
.cm-s-default .cm-variable-3 {
  color: #b07b46
}

.cm-s-default .cm-comment {
  color: #9aaec1
}

.cm-s-default .cm-string {
  color: #29a634
}

.cm-s-default .cm-string-2 {
  color: #f50
}

.cm-s-default .cm-meta {
  color: #5f7e9c
}

.cm-s-default .cm-qualifier {
  color: #5f7e9c
}

.cm-s-default .cm-builtin {
  color: #0097a7
}

.cm-s-default .cm-tag {
  color: #170
}

.cm-s-default .cm-attribute {
  color: #db2c6f
}

.cm-s-default .cm-hr {
  color: #5f7e9c
}

.cm-s-default .cm-link {
  color: #032f62;
  text-decoration: underline
}

.cm-s-default .cm-error {
  color: #f33f12
}

.cm-invalidchar {
  color: #f33f12
}

.CodeMirror-composing {
  border-bottom: 2px solid
}

div.CodeMirror span.CodeMirror-matchingbracket {
  color: #d99e0b
}

div.CodeMirror span.CodeMirror-nonmatchingbracket {
  color: #f33f12
}

.CodeMirror-matchingtag {
  background: rgba(255, 201, 64, .3)
}
'''

FIX_PERMISSIONS_IN_CONTAINER = """#!/bin/bash
set -e
for d in \$@; do
    find "\$d" \\
    ! \( \\
        -group 1002 \\
        -a -perm -g+rwX  \\
    \) \\
    -exec chgrp 1002 {} \; \\
    -exec chmod g+rwX {} \;
    find "\$d" \\
    \( \\
        -type d \\
        -a ! -perm -6000  \\
    \) \\
    -exec chmod +6000 {} \;
done
"""


# IFRAME_EXTENSION_JS = """define(function () {
#   console.log("This is iframe extension");
#   function _on_load() {
#     console.log("Heihei, the iframe extension has been loaded, the scrollHeight is: ",
#     document.documentElement.scrollHeight || document.body.scrollHeight);
#     window.onload = function () {
#       window.parent.postMessage({
#         type: 'auto',
#         data: document.documentElement.scrollHeight || document.body.scrollHeight
#       }, '*');
#     }
#     window.onhashchange = function () {
#       window.parent.postMessage({
#         type: 'auto',
#         data: document.documentElement.scrollHeight || document.body.scrollHeight
#       }, '*');
#     }
#     window.onbeforeunload = function () {
#       window.parent.postMessage({
#         type: 'auto',
#         data: document.documentElement.scrollHeight || document.body.scrollHeight
#       }, '*');
#     }
#   }
#   return {
#     load_ipython_extension: _on_load
#   };
# })"""


# make notebook can run correctly in <iframe> (adaptive height)
IFRAME_CUSTOM_JS = """
    console.log("Heihei, the iframe has been hacked, the scrollHeight is: ",
        document.documentElement.scrollHeight || document.body.scrollHeight);
    window.onload = function () {
        window.parent.postMessage({
            type: 'auto',
            data: document.documentElement.scrollHeight || document.body.scrollHeight
        }, '*');
    }
    window.onhashchange = function () {
        window.parent.postMessage({
            type: 'auto',
            data: document.documentElement.scrollHeight || document.body.scrollHeight
        }, '*');
    }
    window.onbeforeunload = function () {
        window.parent.postMessage({
            type: 'auto',
            data: document.documentElement.scrollHeight || document.body.scrollHeight
        }, '*');
    }
"""

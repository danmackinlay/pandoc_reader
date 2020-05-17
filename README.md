pandoc_reader
=============

A pandoc [markdown] reader plugin for [pelican].
This enables you to use all the pandoc markdown, including (especially) `pandoc-citeproc` enabling an integrated citation workflow.

TODO
------

* Select CSL in a setting

Requirements
------------

  - [pandoc] in $PATH
  - [PyYAML] installed if you want to parse [YAML metadata]

Installation
------------

Instructions for installation of pelican plugins can be obtained from the [pelican plugin manual](https://github.com/getpelican/pelican-plugins/blob/master/Readme.rst).


Configuration
-------------

Additional command line parameters can be passed to pandoc via the PANDOC_ARGS parameter.

    PANDOC_ARGS = [
      '--mathjax',
      '--smart',
      '--toc',
      '--toc-depth=2',
      '--number-sections',
    ]

Pandoc's markdown extensions can be enabled or disabled via the
PANDOC_EXTENSIONS parameter.

    PANDOC_EXTENSIONS = [
      '+hard_line_breaks',
      '-citations'
    ]


YAML Metadata
-------------

No configuration is required to use YAML metadata. Simply include it at the top
of your post, started by `---` and terminated by `---` or `...`. If PyYAML is
not installed, the data will be parsed by the normal metadata parser instead.
For example:

    ---
    title: Using YAML with Pandoc!
    author: Your Name
    date: 2015-05-15 14:07
    description: >
        You can include long, multiline descriptions which
        can wrap across multiple lines (and will be joined
        by YAML).
    complex:
        - or complex data structures
        - like lists
    ...

Contributing
------------

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request


[markdown]: http://daringfireball.net/projects/markdown/
[pandoc]: http://johnmacfarlane.net/pandoc/
[pelican]: http://getpelican.com
[PyYAML]: http://pyyaml.org/
[YAML metadata]: http://pandoc.org/README.html#extension-yaml_metadata_block

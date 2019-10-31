import logging
import subprocess

from pelican import signals
from pelican.readers import BaseReader
from pelican.utils import pelican_open
import os
yaml = None
try:
    from ruamel.yaml import YAML
    yaml = YAML(typ='rt')
except ImportError:
    logging.warning("YAML is not installed; the YAML reader will not work.")


class PandocReader(BaseReader):
    enabled = True
    file_extensions = ['md', 'markdown', 'mkd', 'mdown']

    def _get_meta_and_content(self, text):
        lines = list(text.splitlines())
        metadata = {}

        use_YAML = lines[0].strip() == '---' and yaml is not None
        if use_YAML:
            # Load the data we need to parse
            to_parse = []
            for i, line in enumerate(lines[1:]):
                # When we find a terminator (`---` or `...`), stop.
                if line.strip() in ('---', '...'):
                    # Do not include the terminator itself.
                    break

                # Otherwise, just keep adding the lines to the parseable.
                to_parse.append(line)

            parsed = yaml.load("\n".join(to_parse))

            # Postprocess to make the data usable by Pelican.
            for k in parsed:
                name, value = k.lower(), parsed[k]
                metadata[name] = self.process_metadata(name, value)

            # Return the text entirely.
            content = "\n".join(lines[(i+2):])

        else:
            for i, line in enumerate(lines):
                kv = line.split(':', 1)
                if len(kv) == 2:
                    name, value = kv[0].lower(), kv[1].strip()
                    metadata[name] = self.process_metadata(name, value)
                else:
                    content = "\n".join(lines[i:])

        return metadata, content

    def read(self, filename):
        with pelican_open(filename) as fp:
            text = fp

        # Although we extract and separate header and body here, we don't use it.
        # pandoc is happy to process a metadata block for itself.
        metadata, content = self._get_meta_and_content(text)

        extensions = self.settings.get('PANDOC_EXTENSIONS', '')
        if isinstance(extensions, list):
            # Assume user supplied + and - delimeters
            extensions = ''.join(extensions)

        pandoc_cmd = ["pandoc", "--from=markdown" + extensions, "--to=html5"]

        filters = self.settings.get('PANDOC_FILTERS', [])
        for filt in filters:
            pandoc_cmd.extend(["--filter={}".format( filt)])

        bib_dir = self.settings.get(
            'PANDOC_BIBDIR',
            os.path.dirname(filename))
        bib_header = self.settings.get(
            'PANDOC_BIBHEADER',
            None)

        extra_args = self.settings.get('PANDOC_ARGS', [])

        if "bibliography" in metadata.keys():
            bib_file = os.path.join(bib_dir, metadata['bibliography'])
            if not os.path.exists(bib_file):
                raise FileNotFoundError(bib_file)
            extra_args = extra_args + ['--bibliography={}'.format(bib_file)]

            if bib_header is not None:
                extra_args = extra_args + [
                    '--metadata=reference-section-title={}'.format(
                        bib_header)]
        pandoc_cmd.extend(extra_args)
        proc = subprocess.Popen(
            pandoc_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

        output, err = proc.communicate(text.encode('utf-8'))
        status = proc.wait()
        output, err = output.decode('utf-8'), err.decode('utf-8')
        if status > 0:
            logging.warning(output + err)

        # Make sure we don't lose Pelican template parameters.
        output = output.replace('%7Battach%7D', '{attach}')\
                       .replace('%7Bfilename%7D', '{filename}')\
                       .replace('%7Bstatic%7D', '{static}')\
                       .replace('%7Btag%7D', '{tag}')\
                       .replace('%7Bcategory%7D', '{category}')

        return output, metadata


def add_reader(readers):
    for ext in PandocReader.file_extensions:
        readers.reader_classes[ext] = PandocReader


def register():
    signals.readers_init.connect(add_reader)

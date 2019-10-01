import subprocess
from pelican import signals
from pelican.readers import BaseReader
from pelican.utils import pelican_open


class PandocReader(BaseReader):
    enabled = True
    file_extensions = ['md', 'markdown', 'mkd', 'mdown']

    def read(self, filename):
        with pelican_open(filename) as fp:
            # text = list(fp.splitlines())
            text = fp

        # Although we extract and separate header and body here, we don't use it.
        # pandoc is happy to process a metadata block for itself.
        metadata, content = self._get_meta_and_content(text)

        bib_dir = self.settings.get(
            'PANDOC_BIBDIR',
            os.path.dirname(filename))

        bib_header = self.settings.get('PANDOC_BIBHEADER', None)

        metadata = {}
        for i, line in enumerate(text):
            kv = line.split(':', 1)
            if len(kv) == 2:
                name, value = kv[0].lower(), kv[1].strip()
                metadata[name] = self.process_metadata(name, value)
            else:
                content = "\n".join(text[i:])
                break

        extra_args = self.settings.get('PANDOC_ARGS', [])
        extensions = self.settings.get('PANDOC_EXTENSIONS', '')
        if isinstance(extensions, list):
            extensions = ''.join(extensions)

        pandoc_cmd = ["pandoc", "--from=markdown" + extensions, "--to=html5"]
        pandoc_cmd.extend(extra_args)

        proc = subprocess.Popen(
            pandoc_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE)

        output = proc.communicate(content.encode('utf-8'))[0].decode('utf-8')
        status = proc.wait()
        if status:
            raise subprocess.CalledProcessError(status, pandoc_cmd)

        return output, metadata


def add_reader(readers):
    for ext in PandocReader.file_extensions:
        readers.reader_classes[ext] = PandocReader


def register():
    signals.readers_init.connect(add_reader)

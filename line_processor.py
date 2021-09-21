
class Processor:
    def __init__(self):
        self.unfinished = ""

    def run(self, line):
        output_lines = []
        if self.unfinished != "":
            line = self.unfinished + line
            self.unfinished = ""
        while True:
            x= line.find("\r\n")
            if x != -1:
                before = line[:x]
                after = line[x+2:]
                output_lines.append(before)
                if before == '':
                    break
                if after == '':
                    break
                line = after
            else:
                self.unfinished = line
                break

        return output_lines

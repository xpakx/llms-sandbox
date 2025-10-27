from string import Template


class Prompt:
    def __init__(
            self,
            filename: str,
    ) -> None:
        self.content = self.load_prompt(filename)

    def load_prompt(self, filename: str) -> str:
        with open(f'prompts/{filename}', 'r') as file:
            content = file.read()
        return content

    def compile(self, args: dict[str, str]) -> str:
        if len(args) == 0:
            return self.content
        template = Template(self.content)
        return template.substitute(**args)

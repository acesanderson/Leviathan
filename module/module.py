from Chain import ChainCLI, arg, Prompt, Chain, Model, ChainCache
from pathlib import Path

# Constants
dir_path = Path(__file__).parent
prompt_path = dir_path / "prompt.jinja2"
db_path = dir_path / ".module.db"
cache = ChainCache(db_name=str(db_path))
Model._chain_cache = cache


class PythonModule(ChainCLI):
    # Just need to override main query function
    @arg("")
    def arg_query(self, param):
        """
        Send a message.
        """
        param = param[0]
        self.messagestore.add_new(role="user", content=param)
        prompt = Prompt(prompt_path.read_text())
        chain = Chain(prompt=prompt, model=self.preferred_model)
        response = chain.run(input_variables={"library_name": param})
        if response.content:
            self.messagestore.add_new(role="assistant", content=str(response.content))
            if self.raw:
                print(response)
            else:
                self._print_markdown(str(response.content))
        else:
            raise ValueError("No response found.")


if __name__ == "__main__":
    p = PythonModule(name="Learn Python Libraries", history_file=".cli_history.log")
    p.run()

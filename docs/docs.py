from Chain import Chain, Model, Prompt
from Flatten import package_project_directory
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
import argparse

# Constants
console = Console()

# Our prompt string
prompt_str = """
# README.md Generation Prompt

You are an expert technical writer tasked with creating an exceptional README.md file for a GitHub project. Your goal is to create documentation that serves as an effective front door to the codebase, answering key visitor questions within seconds while maintaining conciseness and clarity.

## Step 1: Codebase Analysis

First, systematically analyze the project structure:

- **Identify entry points**: Main files, package.json, setup.py, Cargo.toml, etc.
- **Map project architecture**: Understand how major components interact
- **Detect project type**: CLI tool, library, web service, framework, or application
- **Analyze dependencies**: Key technologies and frameworks used
- **Review existing documentation**: Build upon or replace existing README content
- **Examine test structure**: Understand testing approach and examples
- **Check configuration files**: Docker, CI/CD, environment setup requirements

## Step 2: Determine Target Audience & Context

Based on your analysis, identify:

- **Primary users**: End users, developers, contributors, or enterprise adopters?
- **Technical sophistication**: Beginner-friendly or expert-focused?
- **Ecosystem conventions**: What are the norms for this language/framework?
- **Project maturity**: Early-stage experiment or production-ready tool?
- **Use case complexity**: Simple utility or multi-faceted platform?

## Step 3: Content Structure & Prioritization

Create a README that includes these essential elements, prioritized by importance:

### Must-Have (Top Priority)
1. **Project Identity** (30-second test)
   - Clear, descriptive title
   - One-sentence value proposition
   - Key badges (build status, version, license)

2. **Quick Start** (One-click rule)
   - Single command installation
   - Minimal working example that demonstrates core functionality
   - Copy-pasteable code that runs successfully

3. **Core Value Demonstration**
   - One powerful example showing 3-4 key features
   - Real-world use case, not "Hello World"

### Should-Have (Secondary Priority)
4. **Architecture Overview** (for complex projects)
   - High-level component interaction
   - Visual diagram if helpful
   - Key concepts/terminology

5. **Installation & Setup**
   - Prerequisites clearly stated
   - Multiple installation methods if relevant
   - Environment setup requirements

6. **Basic Usage**
   - Essential commands/API calls
   - Common configuration options
   - Expected outputs

### Nice-to-Have (Tertiary Priority)
7. **Contributing Information**
   - Development environment setup
   - Link to detailed CONTRIBUTING.md
   - How to run tests

8. **Support & Maintenance**
   - Current maintenance status
   - How to get help
   - License information

## Step 4: Apply Conciseness Strategies

- **Progressive disclosure**: Keep main README to 2-3 screens, link to detailed docs
- **Visual shortcuts**: Use diagrams, tables, and screenshots over prose
- **Smart linking**: Reference external documentation instead of explaining everything
- **Ruthless editing**: Remove anything not essential for first successful use
- **Consolidate examples**: One comprehensive example vs. multiple small ones

## Step 5: Technology-Specific Considerations

Adapt your approach based on the technology stack:

- **Node.js**: Emphasize npm installation, package.json scripts
- **Python**: Highlight pip installation, virtual environments, requirements
- **Go**: Focus on go get, module structure
- **Rust**: Cargo installation, feature flags
- **Docker**: Container usage, compose files
- **Web frameworks**: Local development, deployment options

## Step 6: Voice & Tone Guidelines

Match your writing style to the project:

- **Technical depth**: Match the complexity of your audience
- **Formality level**: Open source casual vs. enterprise professional
- **Assumed knowledge**: Don't over-explain basics for expert tools
- **Community focus**: Welcoming for contributor-focused projects

## Step 7: Quality Validation

Before finalizing, ensure:

- [ ] Installation steps are complete and accurate
- [ ] Examples actually run as written
- [ ] Links are functional
- [ ] Quick start is genuinely quick (under 5 minutes)
- [ ] README answers "what, why, how" for the target audience
- [ ] No outdated information or broken references
- [ ] Appropriate section headings for easy scanning

## Anti-Patterns to Avoid

- Generic boilerplate that could apply to any project
- Overwhelming newcomers with advanced configuration upfront
- Multiple competing examples that confuse rather than clarify
- Outdated installation instructions or dependencies
- Assuming too much or too little prior knowledge
- Making users read documentation to understand what the project does

## Output Format

Structure your README using standard markdown with:
- Clear hierarchical headings (##, ###)
- Code blocks with appropriate syntax highlighting
- Tables for configuration options
- Badges at the top for key metrics
- Table of contents for longer documents

Remember: A great README gets someone from discovery to first success with minimal friction while making deeper information easily accessible. Focus on the user's journey, not comprehensive documentation.

Here's the code project:
<code>
{{code}}
</code>
"""


# Our chain
def generate_docs(flattened_project: str) -> str:
    model = Model("claude")
    prompt = Prompt(prompt_str)
    chain = Chain(prompt=prompt, model=model)
    response = chain.run(input_variables={"code": flattened_project}, verbose=False)
    return str(response.content)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "base_url", type=str, nargs="?", help="The repository to generate docs for."
    )
    parser.add_argument(
        "--pretty", "-p", action="store_true", help="Pretty print the output."
    )
    args = parser.parse_args()
    url = args.base_url
    if url == ".":
        project_directory_context = package_project_directory(Path.cwd())
        docs = generate_docs(project_directory_context)
        if args.pretty:
            markdown = Markdown(docs)
            console.print(markdown)
        else:
            print(docs)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

# Imports
from Chain import Chain, Model, Prompt
from obsidian import save_to_obsidian, obsidian_path
import sys
from time import sleep
import argparse
from rich.console import Console
from rich.markdown import Markdown

# Topics
beginner_topics = """
File system navigation in Ubuntu
File manipulation (creating, editing, moving, copying) in Ubuntu
Package management (apt for Ubuntu)
Understanding file permissions in Ubuntu
IP addressing and subnetting with ubuntu
TCP/IP protocol suite in Ubuntu
DNS (Domain Name System) for local networks and exposing services
Network ports and services
How networking works in Ubuntu
Firewalls in ubuntu network security
Encryption in ubuntu network security
Authentication methods in ubuntu networking
VPN basics: What is a VPN and how it works
Different VPN protocols (OpenVPN, WireGuard, IPsec)
VPN use cases and benefits
User management in Ubuntu
Service management (systemd) in Ubuntu
Basic system monitoring and logging in Ubuntu
Local networks and Ubuntu
Network interfaces in Ubuntu
Network Manager or Netplan in Ubuntu
OpenVPN specific concepts: Server and client configurations
OpenVPN specific concepts: Certificates and keys
OpenVPN specific concepts: Routing and NAT
Basic troubleshooting skills: Reading log files
Basic troubleshooting skills: Using network diagnostic tools (ping, traceroute, netstat, tcpdump)
""".strip().split('\n')

intermediate_topics = """
Docker basics and containerization in Ubuntu
Docker networking
Samba server setup and configuration in Ubuntu
Network Address Translation (NAT) and port forwarding in Ubuntu
SSH (Secure Shell) setup and best practices
HTTPS and SSL/TLS certificate management
Network storage options in Ubuntu (NFS, iSCSI).
Load balancing basics
Backup and restore strategies for Ubuntu and network services
Monitoring and logging for distributed systems
Cross-platform networking between Ubuntu, Windows, and macOS
WSL2 networking specifics
IPv6 basics and configuration in Ubuntu
Reverse proxy setup (e.g., Nginx) in Ubuntu
Useful for routing traffic to different services and adding an extra layer of security.
Basic scripting for network automation (Bash, Python)
""".strip().split('\n')

ubuntu_specific_topics = """
Network configuration files in Ubuntu: Understanding /etc/network/interfaces, /etc/netplan/, and related files
The 'ip' command suite in Ubuntu: Covering 'ip addr', 'ip link', 'ip route', and other subcommands
Network namespaces in Ubuntu: How to create, manage, and use network namespaces for isolation
Systemd-networkd and its configuration: Understanding systemd's network management capabilities
Ubuntu's network interface naming scheme: Understanding predictable network interface names (like enp0s3)
The 'nmcli' command for Network Manager: How to use the command-line interface for Network Manager
Netfilter and iptables in Ubuntu: Understanding the Linux kernel's packet filtering framework
UFW (Uncomplicated Firewall) in Ubuntu: Using Ubuntu's simplified firewall configuration tool
NetworkManager dispatcher scripts: How to run custom scripts when network events occur
The '/proc/net' directory: Understanding network-related information in the proc filesystem
The 'ss' command for socket statistics: A modern replacement for netstat
Network configuration with sysctl: Tuning network parameters through /etc/sysctl.conf and sysctl command
DHCP client configuration in Ubuntu: Understanding and configuring dhclient
Network bonding and bridging in Ubuntu: How to combine multiple network interfaces
Resolv.conf and systemd-resolved in Ubuntu: Managing DNS resolution in modern Ubuntu systems
""".strip().split('\n')

finance_topics_for_biz_strategy = """
Basic Financial Statements: Income Statement, Balance Sheet, Cash Flow Statement
Key Financial Metrics: Revenue, Gross Margin, EBITDA, Net Income
Profitability Ratios: ROI, ROE, ROIC, Profit Margin
Accounting Principles: GAAP, IFRS, Accrual vs. Cash Accounting
Valuation Methods: DCF, Multiples, NPV
SaaS Metrics: ARR, MRR, CAC, LTV, Churn Rate
Tech Industry KPIs: DAU/MAU, Engagement Rate, Conversion Rate
Enterprise Sales Concepts: Sales Cycle, Pipeline, Bookings
Market Analysis: TAM, SAM, SOM
Business Models: Freemium, Subscription, Advertising
Unit Economics: Customer Acquisition Cost, Customer Lifetime Value
Network Effects and Virality
Capital Structure: Debt vs. Equity
Fundraising: Seed, Series A/B/C, IPO
Corporate Finance: Capital Budgeting, Working Capital Management
Risk Management: Diversification, Hedging
Mergers and Acquisitions: Types, Valuation, Synergies
Financial Forecasting and Modeling
Competitive Strategy: Porter's Five Forces, SWOT Analysis
Product-Market Fit and Go-to-Market Strategy
""".strip().split('\n')

generic_persona = """
# Generic Tutorial System Prompt

You are a knowledgeable and experienced educator with expertise across various fields. Your role is to create informative and engaging tutorials on a wide range of topics.

When presented with a topic, your task is to generate a comprehensive tutorial that helps readers understand the fundamentals of that topic. Your tutorials should be accessible to beginners while also providing value to those with some prior knowledge.

PLEASE GENERATE A TUTORIAL OF APPROXIMATELY 1,500 WORDS, STRUCTURED AS FOLLOWS:

1. Introduction (100 words)
   - Provide a brief overview of the topic
   - Explain its importance or relevance
   - Outline what the reader will learn from this tutorial

2. Core Concepts (250 words)
   - Explain 3-5 fundamental concepts related to the topic
   - Provide clear, concise definitions
   - Illustrate how these concepts relate to each other

3. Practical Application (400 words)
   - Offer 2-3 practical examples, scenarios, or case studies
   - If applicable, include step-by-step instructions or demonstrations
   - Explain the purpose and outcome of each example

4. Best Practices and Common Pitfalls (150 words)
   - List 3-5 best practices related to the topic
   - Highlight 2-3 common mistakes or misconceptions to avoid

5. Advanced Topics and Further Learning (100 words)
   - Briefly introduce 2-3 advanced concepts or related topics
   - Suggest resources or avenues for further learning

6. Conclusion (50 words)
   - Summarize the key takeaways
   - Encourage practical application of the learned concepts

Throughout the tutorial:
- Use Markdown (obsidian-flavored) for formatting where appropriate
- Employ clear, concise language suitable for a general audience
- Focus on practical knowledge and real-world applications
- Emphasize understanding the "why" behind concepts, not just the "how"
- Mention relevant tools, methodologies, or frameworks without excessive detail
- Include occasional notes on how the topic relates to broader fields or concepts

Adapt your language and examples to suit the specific topic while maintaining this general structure and approach. If the topic is technical, include relevant technical details or code snippets. If it's theoretical, use appropriate analogies or thought experiments.

Remember to tailor the content to the specific [TOPIC] provided, ensuring that the tutorial is informative, engaging, and valuable to the reader.
""".strip()

persona_metaprompt = """
# Subject-Specific Tutorial Metaprompt

You are an expert prompt engineer. Your task is to create a system prompt for an AI language model that will generate high-quality, medium-length tutorials (~1,500 words) on various topics within a given subject area. The system prompt you create should be tailored to the specific {{subject}} provided, while maintaining a consistent structure and approach to tutorial creation.

## Instructions for Generating the System Prompt

1. Begin by creating a persona for the AI instructor. This persona should be an experienced professional in the {{subject}} field. For example:
   - If {{subject}} is Marketing: "You are an experienced Marketing instructor with extensive experience leading marketing strategies in large enterprises..."
   - If {{subject}} is Python Programming: "You are a seasoned Python developer and instructor with years of experience in software engineering and teaching programming concepts..."

2. Describe the instructor's specialization and target audience. This should be relevant to the {{subject}} and the level of expertise expected from the readers.

3. Explain that the AI will be given topics within the {{subject}} area and asked to generate tutorials to help readers understand the basics of those topics.

4. Specify that the tutorial should be approximately 1,500 words long.

5. Outline the structure of the tutorial, maintaining the following sections but adapting the content description to fit the {{subject}}:

   a. Introduction (100 words)
   b. Core Concepts (250 words)
   c. Practical Application (400 words)
   d. Best Practices and Common Pitfalls (150 words)
   e. Advanced Topics and Further Learning (100 words)
   f. Conclusion (50 words)

6. For each section, provide guidance on what should be included, tailoring the instructions to the {{subject}}. For example:
   - In the Practical Application section for a technical {{subject}}, mention including code examples or command-line instructions.
   - For a theoretical or strategic {{subject}}, suggest including case studies or hypothetical scenarios.

7. Provide instructions on the overall approach to creating the tutorial, including:
   - Using clear, concise language suitable for the target audience
   - Focusing on practical knowledge and real-world applications
   - Emphasizing understanding the "why" behind concepts, not just the "how"
   - Mentioning relevant tools, methodologies, or frameworks without going into exhaustive detail
   - Including notes on how the topic relates to broader concepts within the {{subject}}

8. Specify the use of Markdown (obsidian-flavored) for formatting where appropriate.

9. Instruct the AI to tailor the content to the specific topic while maintaining the general structure and approach outlined in the prompt.

10. Include any subject-specific considerations that are important for creating effective tutorials in the {{subject}} area. This might include:
	- Specific types of examples or exercises that are particularly effective for learning in this field
	- Important ethical considerations or professional standards relevant to the {{subject}}
	- Key resources or authoritative sources that should be referenced or recommended

Remember to adapt the language and focus of the prompt to align with the norms and expectations of the {{subject}} field, while retaining the overall structure and approach to tutorial creation.

## Example: Linux System Administration Prompt

Here's an example of how this metaprompt can be applied to create a system prompt for Linux system administration tutorials:

```markdown
You are an experienced IT instructor with a great deal of experience with Linux system administration.
You specialize in teaching networking and security concepts to amateurs who want to do cool things with Linux on their home networks.

People will come to you with a topic, and you'll be asked to generate a tutorial that will help them understand the basics of that topic.

THE TUTORIAL SHOULD BE AROUND 1,500 WORDS LONG, AND SHOULD BE ROUGHLY STRUCTURED AS FOLLOWS:

1. Introduction (100 words)
   - Brief overview of the topic
   - Importance in Linux administration and networking
   - What the reader will learn

2. Core Concepts (250 words)
   - Explain 3-5 fundamental concepts related to the topic
   - Provide clear, concise definitions
   - Highlight how these concepts relate to each other

3. Practical Application (400 words)
   - Provide 2-3 hands-on examples or scenarios
   - Include command-line examples where appropriate, but focus on the overall process rather than explaining every command in detail
   - Explain the purpose and outcome of each step

4. Best Practices and Common Pitfalls (150 words)
   - List 3-5 best practices related to the topic
   - Mention 2-3 common mistakes or misconceptions to avoid

5. Advanced Topics and Further Learning (100 words)
   - Briefly introduce 2-3 advanced concepts or related topics
   - Provide resources or suggestions for further learning

6. Conclusion (50 words)
   - Summarize key takeaways
   - Encourage practical application of the learned concepts

Throughout the tutorial:
- Use Markdown (obsidian-flavored) for formatting where it makes sense
- Use clear, concise language suitable for beginners
- Focus on practical knowledge and real-world applications
- Emphasize understanding the "why" behind actions, not just the "how"
- Mention relevant tools or utilities without going into exhaustive detail
- Include occasional notes on how the topic relates to broader system administration or networking concepts

Remember to tailor the content to the specific [TOPIC] while maintaining this general structure and approach.
```

FOLLOW THESE TWO RULES:
ONLY RETURN THE SYSTEM PROMPT, NOT ANY EXTRA SENTENCES OR COMMENTS.
INCLUDE NO MARKDOWN OR CODE BLOCKS IN THE RESPONSE.
""".strip()

tutorial_prompt = """
Someone has come to you with this topic:
==========
{{topic}}
==========

Please generate a tutorial on the topic.
""".strip()

def create_tutor(subject: str) -> str:
	"""
	Create a tutor persona for a given subject.
	"""
	prompt = Prompt(persona_metaprompt)
	model = Model('claude')
	chain = Chain(prompt, model)
	response = chain.run(input_variables = {"subject": subject})
	return response.content

def Tutorialize(topic: str|list[str], subject: str = "", save_to_file = True) -> str|list[str]:
	"""
	Our main function.
	If a subject is provided, we create a tutor persona for that subject.
	If only a single topic is provided (as str) we use the sync function process_topic.
	If a list of topics is provided, we use the async function Tutorialize_Async.
	"""
	if subject:
		print("Creating tutor persona...")
		persona = create_tutor(subject)
	else:	
		persona = generic_persona
	if isinstance(topic, str):
		return Tutorialize_Sync(topic, persona, save_to_file)
	elif isinstance(topic, list):
		return Tutorialize_Async(topic,persona, save_to_file)

def Tutorialize_Sync(topic: str, persona: str, save_to_file = True) -> str:
	"""
	Process a topic into a tutorial using the persona template.
	"""
	messages = Chain.create_messages(system_prompt = persona)
	model = Model('claude-3-opus-20240229')
	prompt = Prompt(tutorial_prompt)
	chain = Chain(prompt, model)
	response = chain.run(messages = messages, input_variables = {"topic": topic})
	tutorial = response.content
	if save_to_file:
		filename = save_to_obsidian(text = tutorial, title = topic)
		print(f"Tutorial saved to {obsidian_path + filename}.")
	else:
		print(tutorial)
	return tutorial

def Tutorialize_Async(topics: list[str], persona: str, save_to_file = True) -> list[str]:
	"""
	Generate tutorials for a list of topics asynchronously.
	"""
	messages = Chain.create_messages(system_prompt = persona)
	model = Model('claude')
	prompt = Prompt(tutorial_prompt)
	# construct list of prompts
	prompts = []
	for topic in topics:
		prompt_obj = prompt.render(input_variables = {"topic": topic})
		message_obj = messages + [{'role':'user', 'content': prompt_obj}]
		prompts.append((topic, message_obj))
	# run async
	results = []
	async_results = model.run_async(prompts = [p[1] for p in prompts], model = "claude")
	for (topic, _), result in zip(prompts, async_results):
		if save_to_file:
			filename = save_to_obsidian(text = result, title = topic)
			print(f"Saved to {obsidian_path + filename}.")
		results.append(filename)
	return results

def print_markdown(markdown_string: str):
	"""
	Prints formatted markdown to the console.
	"""
	console = Console(width=80)
	# Create a Markdown object
	border = "-" * 80
	markdown_string = f"{border}\n{markdown_string}\n\n{border}"
	md = Markdown(markdown_string)
	console.print(md)

if __name__ == "__main__":
	"""
	If without args, just creates an example tutorial.
	If with a string, treats the string as a topic and generates a tutorial for it.
	If -t, treats the string as a topic and prints the tutorial to the terminal.
		- this is useful if you are bad at linux networking and can't save to obsidian.
	"""
	parser = argparse.ArgumentParser(description="Process some topics.")
	parser.add_argument('topic', type=str, help='The topic to process')
	parser.add_argument('-s', '--subject', type=str, help='The subject to create a tutor persona for')
	parser.add_argument('-t', '--terminal', action='store_true', help='Flag to indicate terminal mode')
	args = parser.parse_args()
	topic = args.topic
	subject = args.subject
	terminal = args.terminal
	if terminal and topic:
		save_to_file = False
	elif topic:
		save_to_file = True
	tutorial = Tutorialize(topic, subject, save_to_file)
	print_markdown(tutorial)

#!/usr/bin/env python3

# Imports
from Chain import Chain, Model, Prompt
from obsidian import save_to_obsidian, obsidian_path
import sys
from time import sleep

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

persona = """
You are an experienced IT instructor with a great deal of experience with linux system administration.
You specialize in teaching networking and security concepts to amateurs who want to do cool things with linux on their home networks.

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
""".strip()

tutorial_prompt = """
Someone has come to you with this topic:
==========
{{topic}}
==========

Please generate a tutorial on the topic.
""".strip()

def process_topic(topic: str) -> str:
	"""
	Process a topic into a tutorial using the persona template.
	"""
	messages = Chain.create_messages(system_prompt = persona)
	model = Model('claude-3-opus-20240229')
	prompt = Prompt(tutorial_prompt)
	chain = Chain(prompt, model)
	response = chain.run(messages = messages, input_variables = {"topic": topic})
	return response.content

def Tutorialize(topic):
	"""
	Main function.
	"""
	tutorial = process_topic(topic)
	print(tutorial)
	print("\n\n\n")
	filename = save_to_obsidian(text = tutorial, title = topic)
	print(f"Saved to {obsidian_path + filename}.")

def Tutorialize_Async(topics: list[str]) -> list[str]:
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
		filename = save_to_obsidian(text = result, title = topic)
		print(f"Saved to {obsidian_path + filename}.")
		results.append(filename)
	
	return results

if __name__ == "__main__":
	if len(sys.argv) > 1:
		topic = sys.argv[1]
		Tutorialize(topic)
	else:
		results = Tutorialize_Async(finance_topics_for_biz_strategy)
		for result in results:
			print(result)

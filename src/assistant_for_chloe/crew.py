from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from typing import Tuple, Union, Dict, Any
import sys

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class AssistantForChloe():
	"""AssistantForChloe crew"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	@agent
	def researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['researcher'],
			memory=True,
			verbose=True,
			tools=[SerperDevTool()]
		)

	@agent
	def reporting_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['reporting_analyst'],
			verbose=True
		)
	
	@agent
	def email_summarizer(self) -> Agent:
		return Agent(
			config=self.agents_config['email_summarizer'],
			verbose=True
		)

	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
		)

	@task
	def reporting_task(self) -> Task:
		return Task(
			config=self.tasks_config['reporting_task'],
			# output_file='report.md'
		)
	
	def validate_email_content(self, result: str) -> Tuple[bool, Union[Dict[str, Any], str]]:
		"""Validates the email content"""
		try:
			print(f'debug in {sys._getframe().f_code.co_name}: {result}, type of input: {type(result)}')
			# Check word count
			word_count = len(result.split())
			if word_count > 200:
				return (False, {
					"error": "Email content exceeds 200 words",
					"code": "WORD_COUNT_ERROR",
					"context": {"word_count": word_count}
				})

			# Additional validation logic here
			return (True, result.strip())
		except Exception as e:
			return (False, {
				"error": "Unexpected error during validation",
				"code": "SYSTEM_ERROR"
			})
	
	
	def validate_email_format(self, result: str) -> Tuple[bool, Union[str, str]]:
		"""Ensure the output contains a valid email address."""
		import re
		email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
		if re.match(email_pattern, result.strip()):
			return (True, result.strip())
		return (False, "Output must be a valid email address")
	
	def filter_sensitive_info(self, result: str) -> Tuple[bool, Union[str, str]]:
		"""Remove or validate sensitive information."""
		sensitive_patterns = ['SSN:', 'password:', 'secret:']
		for pattern in sensitive_patterns:
			if pattern.lower() in result.lower():
				return (False, f"Output contains sensitive information ({pattern})")
		return (True, result)
	
	def normalize_phone_number(self, result: str) -> Tuple[bool, Union[str, str]]:
		"""Ensure phone numbers are in a consistent format."""
		import re
		digits = re.sub(r'\D', '', result)
		if len(digits) == 10:
			formatted = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
			return (True, formatted)
		return (False, "Output must be a 10-digit phone number")

	def chain_validations(self, *validators):
		"""Chain multiple validators together."""
		def combined_validator(result):
			for validator in validators:
				success, data = validator(result)
				if not success:
					return (False, data)
				result = data
			return (True, result)
		return combined_validator

	@task
	def email_summarization_task(self) -> Task:
		return Task(
			config=self.tasks_config['email_summarizer_task'],
			output_file='email_summary.txt',
			guardrail=self.chain_validations(
				self.validate_email_content,
				self.validate_email_format,
				self.filter_sensitive_info
    		)
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the AssistantForChloe crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)

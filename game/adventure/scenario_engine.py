class ScenarioEngine:
    def __init__(self, script, api_scenario):
        self.script = script
        self.api_scenario = api_scenario

        self.steps = script["steps"]
        self.current_step_index = 0

        self.clues_correct = 0
        self.clues_answered = 0
        self.clue_score = 0
        self.points_per_correct_clue = 5

        self.feedback_message = ""
        self.feedback_correct = False
        self.showing_clue_feedback = False

        self.finished = False

    @property
    def current_step(self):
        if self.current_step_index >= len(self.steps):
            return None

        return self.steps[self.current_step_index]

    def advance_dialogue(self):
        step = self.current_step

        if not step or step["type"] != "dialogue":
            return

        self.current_step_index += 1

    def answer_clue(self, selected_index):
        step = self.current_step

        if not step or step["type"] != "clue":
            return

        self.clues_answered += 1

        self.feedback_correct = (
                selected_index == step["correct_answer"]
        )

        if self.feedback_correct:
            self.clues_correct += 1
            self.clue_score += self.points_per_correct_clue
            self.feedback_message = step["correct_feedback"]
        else:
            self.feedback_message = step["wrong_feedback"]

        self.showing_clue_feedback = True

    def close_clue_feedback(self):
        if not self.showing_clue_feedback:
            return

        self.showing_clue_feedback = False
        self.feedback_message = ""
        self.current_step_index += 1

    def is_final_step(self):
        step = self.current_step
        return bool(step and step["type"] == "final")

    def get_final_actions(self):
        return self.api_scenario.get("actions", [])

    def complete(self):
        self.finished = True
from abc import ABC, abstractmethod


class State(ABC):
    def __init__(self):
        self.next_states = []

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """
        function checks whether occured character is handled by current ctate
        """

    def check_next(self, next_char: str):
        for state in self.next_states:
            if state.check_self(next_char):
                return state
        raise NotImplementedError("rejected string")


class StartState(State):
    def check_self(self, char):
        return True


class TerminationState(State):
    def check_self(self, char):
        return False


class DotState(State):
    """
    state for . character (any character accepted)
    """
    def check_self(self, char: str):
        return True


class AsciiState(State):
    """
    state for alphabet letters or numbers
    """

    def __init__(self, symbol: str):
        super().__init__()
        self.symbol = symbol

    def check_self(self, char: str):
        return char == self.symbol

class StarState(State):
    def __init__(self, checking_state):
        super().__init__()
        self.next_states.append(self)
        self.checking_state = checking_state
    
    def check_self(self, char):
        return self.checking_state.check_self(char)

class PlusState(State):
    def __init__(self, checking_state):
        super().__init__()
        self.next_states.append(self)
        self.checking_state = checking_state
    
    def check_self(self, char):
        return self.checking_state.check_self(char)
    
class GroupState(State):
    def __init__(self, group):
        super().__init__()
        self.accepted_chars = set()
        i = 0
        while i < len(group):
            char = group[i]
            self.accepted_chars.add(char)
            if i + 1 < len(group):
                if group[i + 1] == "-":
                    start = ord(group[i])
                    if i + 2 >= len(group) or group[i + 2] == '-':
                        raise ValueError(f"Invalid range syntax in group [{group}]")
                    end = ord(group[i + 2])
                    if start > end:
                        raise ValueError(f"Invalid range values in group [{group}]")
                    self.accepted_chars.update(map(chr, range(start, end + 1)))

                    i += 2
            i += 1

    
    def check_self(self, char):
        return char in self.accepted_chars


class RegexFSM:
    def __init__(self, pattern: str):
        self.start_state = StartState()
        current_state = self.start_state

        i = 0

        while i < len(pattern):
            char = pattern[i]

            if char == ".":
                new_state = DotState()
            elif char == "[":
                end = pattern.find("]")
                if end == -1:
                    raise ValueError("Group never closed")
                group = pattern[i + 1 : i + end]
                i += len(group) + 1
                new_state = GroupState(group)
            elif char.isascii():
                new_state = AsciiState(char)
            else:
                raise ValueError(f"Character {pattern[i]} is not supported.")

            if i + 1 < len(pattern):
                if pattern[i + 1] == "*":
                    new_state = StarState(new_state)
                    i += 1
                elif pattern[i + 1] == "+":
                    new_state = PlusState(new_state)
                    i += 1

            current_state.next_states.append(new_state)
            current_state = new_state

            i += 1

        current_state.next_states.append(TerminationState())

    def check_string(self, string):
        def dfs(state, i):
            for next_state in state.next_states:
                if isinstance(next_state, StarState) and next_state != state:
                    if dfs(next_state, i):
                        return True
                elif i < len(string) and next_state.check_self(string[i]):
                    if dfs(next_state, i + 1):
                        return True
                elif i >= len(string) and isinstance(next_state, TerminationState):
                    return True

            return False

        return dfs(self.start_state, 0)

if __name__ == "__main__":
    regex_pattern = "[asdaf-px-z]*a"

    regex_compiled = RegexFSM(regex_pattern)

    print(regex_compiled.check_string("aaaaaa4uhi"))  # True
    print(regex_compiled.check_string("a"))  # True
    print(regex_compiled.check_string("yyyyya"))  # True

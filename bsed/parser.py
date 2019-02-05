import abc

from .token_tree import TokenNode, TokenTree, Keyword, InputType, keyword_to_user_input_type


class TranslatorInterface(abc.ABC):
    @abc.abstractmethod
    def translate(self, formatted_cmd, input_args: dict, translation_file: str) -> str:
        pass


class Parser:
    def __init__(self, translator: TranslatorInterface, token_trees: dict):
        self.translator = translator
        self.trees = token_trees

    def parse_expression(self, command_statement: [str], node: TokenNode) -> (str, dict):
        if len(command_statement) == 0:
            return None, None
        input_vars = {}
        cmd_words = []
        words_consumed = 0

        def next_step(remaining_commands):
            for child_node in sorted(node.children.values(), key=lambda n: -int(n.is_sub_expression())):
                res, args = self.parse_expression(remaining_commands, child_node)
                if res is not None:
                    return res, args
            return None, None

        if node.is_root():
            return next_step(command_statement)

        expr_identifier = Keyword.expr_key_to_identifier(node.text)
        if expr_identifier is not None:
            nested_expression, words_consumed = self.translate_expression(command_statement, expr_identifier)
            if nested_expression is None:
                return None, None
            input_vars[node.var_name] = nested_expression
            cmd_words.append('{%s}' % node.var_name)
        else:
            input_type = keyword_to_user_input_type(node.text)
            if input_type is None:
                input_type = InputType.COMMAND
            arg = input_type.validated_and_formatted(command_statement[0])
            if arg is None:
                return None, None
            if input_type is InputType.COMMAND:
                if arg != node.text:
                    return None, None
                cmd_words.append(arg)
            else:
                input_vars[node.var_name] = arg
                cmd_words.append(input_type.token_str())
            words_consumed = 1
        if not node.terminates_command():
            remaining_cmd_words, remaining_inputs = next_step(command_statement[words_consumed:])
            if remaining_cmd_words is None:
                return None, None
            cmd_words = cmd_words + remaining_cmd_words
            input_vars.update(remaining_inputs)
        return cmd_words, input_vars

    def translate_expression(self, command_statement, tree_identifier=Keyword.ROOT_TREE.value, extra_args=None) -> (str, int):
        if isinstance(command_statement, str):
            command_statement = command_statement.split()
        if not isinstance(command_statement, list):
            raise TypeError
        cmd, args = self.parse_expression(command_statement, self.trees[tree_identifier].root)
        if cmd is None:
            return None, None
        translation_file_name = self.trees[tree_identifier].translation_file
        # TODO: Validate argument relationships (e.g. start < end)
        if extra_args is not None:
            args.update(extra_args)
        words_consumed = len(cmd)
        return self.translator.translate(cmd, args, translation_file_name), words_consumed

    def possible_next_vals(self, command_statement: [str], prefix: str, tree_identifier=Keyword.ROOT_TREE.value):

        def print_node_list(children, prefix=''):
            print(prefix + ' ' + str([c.text for c in children]))

        def get_next_layer(node):
            print('!#@$!@#%!@#%!@   ', str(node))
            res = []
            subtree_ids = set()
            for c in node.children.values():
                if not c.is_sub_expression():
                    res.append(c)
                else:
                    subtree_ids.add(Keyword.expr_key_to_identifier(c.text))
            print(subtree_ids)
            res += [c for tid in subtree_ids for c in self.trees[tid].root.children.values()]
            return res

        nodes = list(self.trees[tree_identifier].root.children.values())
        print('#########', nodes)
        print('>>>>>>>>> command_statement:', command_statement)
        for token in command_statement:
            next_layer = []
            print_node_list(nodes, prefix='nodes:')
            while len(nodes) > 0:
                n = nodes.pop(0)
                assert isinstance(n, TokenNode)
                if not (n.text == token.lower() or n.is_sub_expression() or n.is_user_input()):
                    continue
                next_layer += get_next_layer(n)
            nodes = next_layer
        print_node_list(nodes)
        # valid_children = [c for c in n.children.values() if c.is_user_input()]
        print_node_list(nodes)
        final_options = [c for c in nodes if not c.is_sub_expression()]
        return [c.text for c in final_options]

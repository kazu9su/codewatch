from astroid.exceptions import InferenceError


class CallNodePredicates(object):
    @staticmethod
    def does_node_call_method(call_node, method_name):
        """
        Returns true if call_node looks like a call to method_name
        Does not do any inference, just matches on the name

        eg:
        for the call node `my.nested.function.call()` it will return true
        for the method_name 'my.nested.function.call'

        will also work if the node looks like `my().nested().function().call()`
        """
        qname_split = method_name.split('.')
        qname_split.reverse()

        current_node = call_node.func
        for expected_name in qname_split[:-1]:
            if hasattr(current_node, "func"):
                current_node = current_node.func
            if not hasattr(current_node, "expr"):
                return False
            if current_node.attrname != expected_name:
                return False
            current_node = current_node.expr
        if (
            not hasattr(current_node, "name") or
            current_node.name != qname_split[-1]
        ):
            return False
        return True

    @staticmethod
    def is_node_qname_inferred(node, expected_qname):
        """
        Perform inference on the node and check for the expected qname
        eg.

        ```
        from my_models import Grade
        grade = Grade()
        ```

        node: An `astroid.nodes.Call` node
        expected_qname: 'my_models.Grade'
        returns: True
        """
        try:
            inferred_types = node.inferred()
        except InferenceError:
            return False
        success = any(
            hasattr(node_type, 'qname') and node_type.qname() == expected_qname
            for node_type in inferred_types
        )
        return success

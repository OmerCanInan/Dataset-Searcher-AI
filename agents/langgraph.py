import streamlit as st


class LangGraphManager:
    def __init__(self, session_state):
        self.session_state = session_state
        self._ensure_state()

    def _ensure_state(self):
        if 'langgraph' not in self.session_state:
            self.session_state['langgraph'] = {'nodes': [], 'edges': []}
        if 'agent_states' not in self.session_state:
            self.session_state['agent_states'] = {
                'hunter': 'idle',
                'parser': 'idle',
                'normalizer': 'idle',
                'final_eda': 'idle'
            }
        if 'current_dataset' not in self.session_state:
            self.session_state['current_dataset'] = None
        for agent in ['hunter', 'parser', 'normalizer', 'final_eda']:
            self.add_node(agent, 'agent', {'status': self.session_state['agent_states'].get(agent, 'idle')})

    def add_node(self, node_id, node_type, metadata=None):
        metadata = metadata or {}
        node = {'id': node_id, 'type': node_type, 'metadata': metadata}
        if node not in self.session_state['langgraph']['nodes']:
            self.session_state['langgraph']['nodes'].append(node)
        return node

    def add_edge(self, source_id, target_id, relation='related_to'):
        edge = {'source': source_id, 'target': target_id, 'relation': relation}
        if edge not in self.session_state['langgraph']['edges']:
            self.session_state['langgraph']['edges'].append(edge)
        return edge

    def update_agent_state(self, agent_name, status):
        if agent_name in self.session_state['agent_states']:
            self.session_state['agent_states'][agent_name] = status
        else:
            self.session_state['agent_states'][agent_name] = status
        return self.session_state['agent_states']

    def set_current_dataset(self, dataset_id):
        self.session_state['current_dataset'] = dataset_id
        self.add_node(dataset_id, 'dataset')
        return dataset_id

    def get_graph(self):
        return self.session_state['langgraph']

    def get_states(self):
        return self.session_state['agent_states']


def init_langgraph_state(session_state):
    return LangGraphManager(session_state)

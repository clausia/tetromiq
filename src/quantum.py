from qiskit import QuantumRegister, \
    ClassicalRegister, \
    QuantumCircuit, \
    execute, \
    Aer


quantum_states = {
    '00': 0,
    '01': 1,
    '10': 2,
    '11': 3
}


def collapse(superposed_blocks):
    """
    The tiles can be separated into up to 4 sub-pieces, in the following combinations:
        - 50% , 50%
        - 50% , 25% , 25%
        - 25% , 25% , 25% , 25%
    That order will be maintained in the sub-piece list so that they can always refer to the same probabilities all the time.

    :param superposed_blocks: One of this possibilities
        - [ block_50 , block_50 , None ,     None ]
        - [ block_50 , block_25 , block_25 , None ]
        - [ block_25 , block_25 , block_25 , block_25 ]

    :return: collapsed block
    """

    case_to_collapse = len(filter(lambda x: x is not None, superposed_blocks))

    return superposed_blocks[{
                2: collapse_two_states,
                3: collapse_three_states,
                4: collapse_four_states
            }[case_to_collapse]()]


def collapse_two_states():
    q = QuantumRegister(2)
    c = ClassicalRegister(2)
    qc = QuantumCircuit(q, c)

    # create a Bell state
    qc.h(0)
    qc.cx(0, 1)

    qc.measure(q, c)

    result_state = list(execute(qc, Aer.get_backend('qasm_simulator'), shots=1).result().get_counts(qc).keys())[0]

    return quantum_states[result_state]


def collapse_three_states():
    q = QuantumRegister(2)
    c = ClassicalRegister(2)
    qc = QuantumCircuit(q, c)

    # apply first Hadamard
    qc.h(0)
    qc.measure(q[0], c[0])

    # apply second Hadamard if the measurement outcome is 0
    qc.x(1)
    qc.h(1).c_if(c, 1)
    qc.measure(q[1], c[1])

    result_state = list(execute(qc, Aer.get_backend('qasm_simulator'), shots=1).result().get_counts(qc).keys())[0]

    return quantum_states[result_state]


def collapse_four_states():
    q = QuantumRegister(2)
    c = ClassicalRegister(2)
    qc = QuantumCircuit(q, c)

    # apply a Hadamard to each qubit
    qc.h(0)
    qc.h(1)
    qc.measure(q, c)

    result_state = list(execute(qc, Aer.get_backend('qasm_simulator'), shots=1).result().get_counts(qc).keys())[0]

    return quantum_states[result_state]


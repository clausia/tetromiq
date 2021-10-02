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


def collapse(quantum_block):
    """
    The tiles can be separated into up to 4 sub-pieces, in the following combinations:
        - 50% , 50%
        - 50% , 25% , 25%
        - 25% , 25% , 50%
        - 25% , 25% , 25% , 25%
    That order will be maintained in the sub-piece list so that they can always refer to the same probabilities all the time.

    :param quantum_block: Its set_blocks attribute has one of this possibilities
        - 2 blocks:
            - [ block_50 , None     , None     , block_50 ]
        - 3 blocks:
            - [ block_50 , block_25 , None     , block_25 ]
            - [ block_25 , None     , block_25 , block_50 ]
        - 4 block
            - [ block_25 , block_25 , block_25 , block_25 ]

    :return: collapsed block
    """

    return quantum_block.set_blocks[{
                2: collapse_two_states,
                3: collapse_three_states,
                4: collapse_four_states
            }[quantum_block.size](quantum_block.set_blocks)]


def collapse_two_states(set_blocks):
    q = QuantumRegister(2)
    c = ClassicalRegister(2)
    qc = QuantumCircuit(q, c)

    # create a Bell state
    qc.h(0)
    qc.cx(0, 1)

    qc.measure(q, c)

    result_state = list(execute(qc, Aer.get_backend('qasm_simulator'), shots=1).result().get_counts(qc).keys())[0]

    print(quantum_states[result_state])
    return quantum_states[result_state]


def collapse_three_states(set_blocks):
    q = QuantumRegister(2)
    c = ClassicalRegister(2)
    qc = QuantumCircuit(q, c)

    if set_blocks.index(None) == 1:
        qc.x(1)
    # apply first Hadamard
    qc.h(0)
    qc.measure(q, c)

    # apply second Hadamard if the measurement outcome is 0
    qc.h(1).c_if(c, 2 if set_blocks.index(None) == 1 else 1)
    qc.measure(q, c)

    result_state = list(execute(qc, Aer.get_backend('qasm_simulator'), shots=1).result().get_counts(qc).keys())[0]

    print(quantum_states[result_state])
    return quantum_states[result_state]


def collapse_four_states(set_blocks):
    q = QuantumRegister(2)
    c = ClassicalRegister(2)
    qc = QuantumCircuit(q, c)

    # apply a Hadamard to each qubit
    qc.h(0)
    qc.h(1)
    qc.measure(q, c)

    result_state = list(execute(qc, Aer.get_backend('qasm_simulator'), shots=1).result().get_counts(qc).keys())[0]

    print(quantum_states[result_state])
    return quantum_states[result_state]


import React from 'react'
import {Form} from 'react-bootstrap'

import RequiredMark from '../marks/RequiredMark'

const SimpleInput = ({label, type, required, onChange}) => {
  return (
    <Form.Group className="mb-3">
      <Form.Label>
        {label}
        <RequiredMark required={required}/>
        </Form.Label>
      <Form.Control
        type={type}
        required={required}
        onChange={onChange}
      />
    </Form.Group>
  )
}

export default SimpleInput
import React from 'react'
import {Form} from 'react-bootstrap'

import RequiredMark from '../marks/RequiredMark'

const ValueInput = ({label, type="text", onChange, value, required=false}) => {
  return (
    <Form.Group className="mb-3">
      <Form.Label className="fs-5">
        {label}
        <RequiredMark required={required} />
      </Form.Label>
      <Form.Control
        type={type}
        onChange={onChange}
        value={value}
        required={required}
      />
    </Form.Group>
  )
}

export default ValueInput
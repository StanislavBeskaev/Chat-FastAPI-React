import React from 'react'
import {Form} from 'react-bootstrap'

const SimpleInput = ({label, type, required, onChange}) => {
  return (
    <Form.Group className="mb-3">
      <Form.Label>
        {label}
        {required
          ? <span style={{color: "red"}}>*</span>
          : null
        }</Form.Label>
      <Form.Control
        type={type}
        required={required}
        onChange={onChange}
      />
    </Form.Group>
  )
}

export default SimpleInput
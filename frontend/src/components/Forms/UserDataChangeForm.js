import React, {useState} from 'react'
import {Button, Form} from 'react-bootstrap'

import ValueInput from '../UI/Inputs/ValueInput'


const UserDataChangeForm = ({onSubmit, currentName, currentSurname}) => {
  const [name, setName] = useState(currentName)
  const [surname, setSurname] = useState(currentSurname)
  const [changed, setChanged] = useState(false)

  const handleNameChange = e => {
    setName(e.target.value)
    if (changed) setChanged(false)
  }

  const handleSurnameChange = e => {
    setSurname(e.target.value)
    if (changed) setChanged(false)
  }

  const handleSubmit = async e => {
    e.preventDefault()
    await onSubmit(name, surname)
    setChanged(true)
  }

  return (
    <Form onSubmit={handleSubmit} className="mb-4" style={{width: '50%'}}>
      <ValueInput
        label="Имя"
        onChange={handleNameChange}
        value={name}
      />
      <ValueInput
        label="Фамилия"
        onChange={handleSurnameChange}
        value={surname}
      />
      <div className="mt-4 d-flex flex-row align-items-center justify-content-end">
        {
          changed
            ? <div className="me-4 text-success">Данные изменены</div>
            : null
        }
        <Button
          variant="primary"
          type="submit"
        >Изменить</Button>
      </div>
    </Form>
  )
}

export default UserDataChangeForm
import React, {useState} from 'react'
import {useHistory} from 'react-router-dom'
import {Button, Form} from 'react-bootstrap'

import store from '../../stores/store'
import ValueInput from '../UI/Inputs/ValueInput'

const ChangeUserDataForm = () => {
  const [name, setName] = useState(store.user.name)
  const [surname, setSurname] = useState(store.user.surname)

  const history = useHistory()

  const handleSubmit = async e => {
    e.preventDefault()
    await store.changeUserData(name, surname)
    //TODO возможно надо перенести в ChangeUserData
    history.push("/user-data/")
  }

  return (
    <Form onSubmit={handleSubmit} className="mb-4">
      <ValueInput
        label="Имя"
        onChange={e => setName(e.target.value)}
        value={name}
      />
      <ValueInput
        label="Фамилия"
        onChange={e => setSurname(e.target.value)}
        value={surname}
      />
      <Button variant="primary" type="submit" className="me-2">Изменить</Button>
    </Form>
  )
}

export default ChangeUserDataForm
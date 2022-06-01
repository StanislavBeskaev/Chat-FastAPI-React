import React from 'react'
import { ListGroup } from 'react-bootstrap'
import contactStore from '../../stores/contactStore'
import {observer} from 'mobx-react-lite'

const Contacts = () => {
  const {contacts} = contactStore

  if (contacts.length === 0) {
    return <div className="m-3">Тут пока пусто</div>
  }

  return (
    <ListGroup variant="flush">
      {contacts.map(contact => (
        <ListGroup.Item key={contact.login}>
          {contact.login}
        </ListGroup.Item>
      ))}
    </ListGroup>
  )
}

export default observer(Contacts)
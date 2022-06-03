import React from 'react'
import {Button, ListGroup} from 'react-bootstrap'
import contactStore from '../../stores/contactStore'
import {observer} from 'mobx-react-lite'

const Contacts = () => {
  const {contacts} = contactStore

  if (contacts.length === 0) {
    return <div className="m-3">Тут пока пусто</div>
  }

  const handleDelete = async (login) => {
    await contactStore.deleteContact(login)
  }

  return (
    <ListGroup variant="flush" className="m-1">
      {contacts.map(contact => (
        <ListGroup.Item key={contact.login}>
          <div className="d-flex justify-content-between">
            <div>{contact.login}</div>
            <Button style={{fontSize: 12}} variant="danger" size="sm" onClick={() => handleDelete(contact.login)}>X</Button>
          </div>
        </ListGroup.Item>
      ))}
    </ListGroup>
  )
}

export default observer(Contacts)
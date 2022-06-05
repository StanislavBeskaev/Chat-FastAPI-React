import React from 'react'
import {Button} from 'react-bootstrap'

import contactModalStore from '../../stores/modals/contactModalStore'
import contactStore from '../../stores/contactStore'


const Contact = ({login, name, surname}) => {

  const handleDelete = async () => {
    //TODO запрашивать подтвереждение на удаление контакта
    await contactStore.deleteContact(login)
  }

  let displayName

  if (name && surname) {
    displayName = `(${name} ${surname})`
  } else if (name && !surname) {
    displayName = `(${name})`
  } else if (!name && surname) {
    displayName = `(${surname})`
  } else {
    displayName = null
  }

  return (
    <div className="d-flex justify-content-between">
      <div
        onClick={() => contactModalStore.showWithLogin(login)}
        style={{cursor: 'pointer'}}
      >
        {login}{displayName}
      </div>
      <Button style={{fontSize: 12}} variant="danger" size="sm" onClick={handleDelete}>X</Button>
    </div>
  )
}

export default Contact

import React from 'react'
import {Button} from 'react-bootstrap'

import contactModalStore from '../../stores/modals/contactModalStore'
import contactStore from '../../stores/contactStore'


const Contact = ({login}) => {

  const handleDelete = async () => {
    //TODO запрашивать подтвереждение на удаление контакта
    await contactStore.deleteContact(login)
  }

  return (
    <div className="d-flex justify-content-between">
      <div
        onClick={() => contactModalStore.showWithLogin(login)}
        style={{cursor: 'pointer'}}
      >
        {contactStore.getDisplayName(login)}
      </div>
      <Button style={{fontSize: 12}} variant="danger" size="sm" onClick={handleDelete}>X</Button>
    </div>
  )
}

export default Contact

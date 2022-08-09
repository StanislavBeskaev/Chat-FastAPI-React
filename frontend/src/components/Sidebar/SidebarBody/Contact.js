import React from 'react'
import {Button} from 'react-bootstrap'

import contactModalStore from '../../../stores/modals/contactModalStore'
import contactStore from '../../../stores/contactStore'
import UserAvatar from '../../Avatars/UserAvatar'
import confirmDeleteModalStore from '../../../stores/modals/confirmDeleteModalStore'


const Contact = ({login}) => {

  const handleDelete = async () => {
    confirmDeleteModalStore.open(
      `Вы точно хотите удалить контакт ${contactStore.getDisplayName(login)} ?`,
      async () => {
        await contactStore.deleteContact(login)
      },
      () => {}
    )
  }

  return (
    <div className="d-flex justify-content-between align-items-center">
      <div
        onClick={() => contactModalStore.showWithLogin(login)}
        style={{cursor: 'pointer'}}
      >
        <div className="d-flex gap-2 align-items-center">
          <UserAvatar login={login} size="sm"/>
          {contactStore.getDisplayName(login)}
        </div>
      </div>
      <Button style={{fontSize: 12}} variant="danger" size="sm" onClick={handleDelete}>X</Button>
    </div>
  )
}

export default Contact

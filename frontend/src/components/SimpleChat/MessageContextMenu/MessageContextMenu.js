import React from 'react'
import {ContextMenu, MenuItem} from 'react-contextmenu'
import {FaRegEdit} from 'react-icons/fa'
import {RiDeleteBin6Line} from 'react-icons/ri'

import './context-menu.css'

import messageContextMenuStore from '../../../stores/messageContextMenuStore'


const MessageContextMenu = () => {

  const onEdit = () => {
    messageContextMenuStore.openMessageEditModal()
  }

  const onDelete = () => {
    messageContextMenuStore.openMessageDeleteModal()
  }

  return (
    <ContextMenu
      id="message-context-menu"
    >
      <MenuItem onClick={onEdit}>
        <FaRegEdit className="text-primary"/>
        <span>Редактировать</span>
      </MenuItem>
      <MenuItem onClick={onDelete}>
        <RiDeleteBin6Line className="text-danger"/>
        <span>Удалить</span>
      </MenuItem>
    </ContextMenu>
  )
}

export default MessageContextMenu

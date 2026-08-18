import pathlib
p = pathlib.Path('./backend/app/api/v1/channels.py')
s = p.read_text(encoding='utf-8')

new_endpoint = '''

@router.delete("/{channel_id}/sources/{source_id}", status_code=204)
async def delete_source(channel_id: str, source_id: str, db: Session = Depends(get_db)):
    """Удалить источник знаний из канала."""
    repo = ChannelRepository(db)
    channel = repo.remove_source(channel_id, source_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel or source not found")
    return None
'''

if '/sources/{source_id}' not in s:
    s += new_endpoint
    p.write_text(s, encoding='utf-8')
    print('✅ Добавлен DELETE /channels/{id}/sources/{source_id}')
else:
    print('ℹ️ Endpoint уже есть')
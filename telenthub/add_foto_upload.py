"""
Script: Adicionar Upload de Foto ao candidato-perfil.html
Injeta funcionalidade de upload de foto usando Supabase Storage.

Como usar:
1. Coloque este arquivo em C:\\Users\\admin\\Desktop\\telenthub\\telenthub\\
2. Execute: python add_foto_upload.py
"""

import re

FILE = 'candidato-perfil.html'

with open(FILE, 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Substituir avatar-edit para ter input file oculto ────────────────────
OLD_AVATAR = '<div class="avatar-edit">🖊 ✏️</div>'
NEW_AVATAR = '''<div class="avatar-edit" onclick="document.getElementById('foto-input').click()" title="Alterar foto">✏️</div>
              <input type="file" id="foto-input" accept="image/*" style="display:none" onchange="uploadFoto(this)">'''

if OLD_AVATAR in html:
    html = html.replace(OLD_AVATAR, NEW_AVATAR)
    print("✅ Botão avatar-edit atualizado")
else:
    # Tentar variação sem emoji específico
    html = re.sub(
        r'<div class="avatar-edit">[^<]*</div>',
        '<div class="avatar-edit" onclick="document.getElementById(\'foto-input\').click()" title="Alterar foto">✏️</div>\n              <input type="file" id="foto-input" accept="image/*" style="display:none" onchange="uploadFoto(this)">',
        html
    )
    print("✅ Botão avatar-edit atualizado (via regex)")

# ── 2. Atualizar exibição do avatar para suportar imagem ────────────────────
OLD_AV_DIV = '<div class="avatar" id="av-initials">?</div>'
NEW_AV_DIV = '<div class="avatar" id="av-initials" style="background-size:cover;background-position:center;background-repeat:no-repeat">?</div>'

if OLD_AV_DIV in html:
    html = html.replace(OLD_AV_DIV, NEW_AV_DIV)
    print("✅ Avatar div atualizado para suportar imagem")

# ── 3. Injetar função uploadFoto no JavaScript ───────────────────────────────
UPLOAD_JS = '''
  // ── Upload de Foto ──────────────────────────────────────────────────────
  async function uploadFoto(input) {
    const file = input.files[0];
    if (!file) return;

    // Validar tamanho (máx 2MB)
    if (file.size > 2 * 1024 * 1024) {
      toast('Foto muito grande. Máximo 2MB.', 'error');
      return;
    }

    // Validar tipo
    if (!file.type.startsWith('image/')) {
      toast('Selecione uma imagem válida.', 'error');
      return;
    }

    toast('Enviando foto...', 'info');

    try {
      const { data: { session } } = await sb.auth.getSession();
      if (!session) return;

      const userId = session.user.id;
      const ext = file.name.split('.').pop();
      const path = `avatars/${userId}/foto.${ext}`;

      // Upload para Supabase Storage
      const { error: uploadError } = await sb.storage
        .from('avatares')
        .upload(path, file, { upsert: true, contentType: file.type });

      if (uploadError) throw uploadError;

      // Obter URL pública
      const { data: { publicUrl } } = sb.storage
        .from('avatares')
        .getPublicUrl(path);

      // Salvar URL no banco
      await sb.from('candidatos')
        .update({ foto_url: publicUrl })
        .eq('user_id', userId);

      // Atualizar visual imediatamente
      const av = document.getElementById('av-initials');
      if (av) {
        av.style.backgroundImage = `url('${publicUrl}')`;
        av.textContent = '';
      }

      toast('Foto atualizada! 📸', 'success');
    } catch (err) {
      console.error(err);
      toast('Erro ao enviar foto. Tente novamente.', 'error');
    }
  }

  // ── Carregar foto salva ──────────────────────────────────────────────────
  async function carregarFotoSalva(fotoUrl, nome) {
    const av = document.getElementById('av-initials');
    if (!av) return;
    if (fotoUrl) {
      av.style.backgroundImage = `url('${fotoUrl}')`;
      av.style.backgroundSize = 'cover';
      av.style.backgroundPosition = 'center';
      av.textContent = '';
    } else if (nome) {
      av.textContent = iniciais(nome);
    }
  }

'''

# Injetar antes do fechamento do script principal
if 'function uploadFoto' not in html:
    # Injetar antes da função toast ou antes do </script> final
    if 'function toast(' in html:
        html = html.replace('function toast(', UPLOAD_JS + '\n  function toast(', 1)
        print("✅ Função uploadFoto injetada")
    else:
        html = html.replace('</script>', UPLOAD_JS + '\n</script>', 1)
        print("✅ Função uploadFoto injetada (fallback)")
else:
    print("⏭️  uploadFoto já existe, pulando")

# ── 4. Chamar carregarFotoSalva após carregar candidato ──────────────────────
# Procurar onde o candidato é carregado e adicionar chamada
if 'carregarFotoSalva' not in html:
    # Injetar após a linha que define iniciais do avatar
    html = html.replace(
        'if(av && nome) av.textContent = iniciais(nome);',
        'if(av && nome) av.textContent = iniciais(nome);\n    await carregarFotoSalva(c?.foto_url, c?.nome);'
    )
    print("✅ Chamada carregarFotoSalva adicionada")

# ── Salvar arquivo ───────────────────────────────────────────────────────────
with open(FILE, 'w', encoding='utf-8') as f:
    f.write(html)

print("\n" + "─"*50)
print("✅ candidato-perfil.html atualizado!")
print("\n⚠️  IMPORTANTE: Crie o bucket no Supabase:")
print("   1. Acesse: https://xroobxmpmeelklegchhs.supabase.co")
print("   2. Storage → New Bucket")
print("   3. Nome: avatares")
print("   4. Public: SIM ✅")
print("\n🚀 Depois faça:")
print("   git add candidato-perfil.html")
print("   git commit -m \"Adicionar upload de foto do candidato\"")
print("   git push origin main")

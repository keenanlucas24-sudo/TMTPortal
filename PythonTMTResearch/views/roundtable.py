import streamlit as st
import pandas as pd
import os
from data.tmt_data import get_roundtable_insights
from db.db_operations import (
    add_roundtable_document, 
    get_roundtable_documents, 
    get_all_tags,
    get_roundtable_tags,
    add_tag,
    add_tag_to_roundtable
)

def show():
    st.title("💡 Roundtable Insights")
    st.markdown("Executive engagement notes and insights from former TMT executives.")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        sector_filter = st.radio(
            "Filter by Sector",
            ["All", "Technology", "Media", "Telecom"]
        )
        
        st.markdown("---")
        
        # Tag filtering
        st.markdown("**Filter by Tags**")
        all_tags = get_all_tags()
        
        # Group tags by category for better UX
        tag_categories = {}
        for tag in all_tags:
            category = tag.get('category', 'Other')
            if category not in tag_categories:
                tag_categories[category] = []
            tag_categories[category].append(tag['name'])
        
        selected_tags = []
        for category, tag_names in sorted(tag_categories.items()):
            with st.expander(f"📁 {category}"):
                for tag_name in sorted(tag_names):
                    if st.checkbox(tag_name, key=f"tag_{tag_name}"):
                        selected_tags.append(tag_name)
        
        st.markdown("---")
        st.markdown("**Quick Stats**")
        roundtables = get_roundtable_insights()
        st.metric("Total Sessions", len(roundtables))
        st.metric("Total Attendees", sum(r["attendees"] for r in roundtables))
    
    with col2:
        # Get roundtables with sector filter
        roundtables = get_roundtable_insights(
            sector_filter if sector_filter != "All" else None
        )
        
        # Apply tag filtering if any tags are selected
        if selected_tags:
            filtered_roundtables = []
            for roundtable in roundtables:
                if "id" in roundtable:
                    roundtable_tags = get_roundtable_tags(roundtable["id"])
                    roundtable_tag_names = [t['name'] for t in roundtable_tags]
                    # Include if roundtable has any of the selected tags
                    if any(tag in roundtable_tag_names for tag in selected_tags):
                        filtered_roundtables.append(roundtable)
            roundtables = filtered_roundtables
        
        roundtables = sorted(roundtables, key=lambda x: x["date"], reverse=True)
        
        if roundtables:
            for idx, roundtable in enumerate(roundtables):
                with st.expander(
                    f"**{roundtable['executive']}** - {roundtable['date'].strftime('%B %d, %Y')}",
                    expanded=(idx == 0)
                ):
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.markdown(f"**Company Background:** {roundtable['company_background']}")
                        st.markdown(f"**Sector:** {roundtable['sector']}")
                        st.markdown(f"**Attendees:** {roundtable['attendees']} participants")
                    
                    with col_b:
                        st.markdown("**Topics Discussed:**")
                        for topic in roundtable["topics"]:
                            st.markdown(f"• {topic}")
                    
                    # Display tags
                    if "id" in roundtable:
                        roundtable_tags = get_roundtable_tags(roundtable["id"])
                        if roundtable_tags:
                            st.markdown("**Tags:**")
                            tag_cols = st.columns(4)
                            for idx, tag in enumerate(roundtable_tags):
                                with tag_cols[idx % 4]:
                                    st.markdown(f"🏷️ `{tag['name']}`")
                    
                    st.markdown("---")
                    st.markdown("**Key Insights:**")
                    st.info(roundtable["key_insights"])
                    
                    st.markdown("**Participating Firms:**")
                    firms_text = ", ".join(roundtable["client_firms"])
                    st.caption(firms_text)
                    
                    st.markdown("---")
                    
                    # Document upload and management section
                    st.markdown("**📎 Documents & Transcripts**")
                    
                    # Display existing documents
                    if "id" in roundtable:
                        documents = get_roundtable_documents(roundtable["id"])
                        
                        if documents:
                            for doc in documents:
                                col_doc1, col_doc2 = st.columns([3, 1])
                                with col_doc1:
                                    st.markdown(f"📄 {doc['filename']}")
                                    st.caption(f"Uploaded: {doc['uploaded_at'].strftime('%Y-%m-%d %H:%M')}")
                                with col_doc2:
                                    # Create download button
                                    if os.path.exists(doc['file_path']):
                                        with open(doc['file_path'], 'rb') as f:
                                            st.download_button(
                                                label="Download",
                                                data=f.read(),
                                                file_name=doc['filename'],
                                                key=f"download_{doc['id']}"
                                            )
                        
                        # File upload section
                        uploaded_file = st.file_uploader(
                            "Upload transcript or document",
                            type=['pdf', 'docx', 'txt', 'md'],
                            key=f"upload_{roundtable['id']}"
                        )
                        
                        if uploaded_file is not None:
                            # Save the file
                            upload_dir = "uploads/roundtables"
                            os.makedirs(upload_dir, exist_ok=True)
                            
                            file_path = os.path.join(upload_dir, f"{roundtable['id']}_{uploaded_file.name}")
                            
                            with open(file_path, 'wb') as f:
                                f.write(uploaded_file.getbuffer())
                            
                            # Save metadata to database
                            try:
                                add_roundtable_document(
                                    roundtable['id'],
                                    uploaded_file.name,
                                    file_path,
                                    uploaded_file.size
                                )
                                st.success(f"✓ Uploaded {uploaded_file.name}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error uploading document: {e}")
                    else:
                        st.caption("Document uploads available once roundtable is saved to database.")
        else:
            st.info("No roundtable sessions found for the selected filter.")
